from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

STATE_SOURCE = "PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_SOURCE_CANDIDATE"
STATE_GODOT = "PASS_BOUNDED_DETERMINISTIC_LEAF_FLUTTER_GODOT_VISUAL_CANDIDATE"
STATE_REVIEW = "PASS_BOUNDED_LEAF_FLUTTER_SAMPLED_REVIEW_SURFACE"
CONTEXTS = ("ground_oblique", "crown_overhead")
KINDS = ("baseline", "flutter")
EPS = 1e-9


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_sapling_leaf_flutter_review.py EVIDENCE_DIR")
    root = Path(sys.argv[1])
    source_path = root / "leaf-flutter-summary.json"
    godot_path = root / "vfx-leaf-flutter-godot-receipt.json"
    head_path = root / "exact-head.txt"
    _require(source_path.exists() and godot_path.exists() and head_path.exists(), "missing exact leaf-flutter evidence")

    source = json.loads(source_path.read_text(encoding="utf-8"))
    godot = json.loads(godot_path.read_text(encoding="utf-8"))
    head = head_path.read_text(encoding="utf-8").strip()
    _require(source.get("state") == STATE_SOURCE, "source candidate is not green")
    _require(godot.get("state") == STATE_GODOT, "Godot candidate is not green")
    _require(godot.get("vfx_head") == head, "Godot receipt/head mismatch")
    _require(len(source.get("samples", [])) == 17 and godot.get("phase_count") == 17, "phase count drifted")
    _require(set(godot.get("contexts", [])) == set(CONTEXTS), "camera contexts drifted")
    _require(len(godot.get("captures", {})) == 68, "capture count drifted")

    images: dict[str, dict[str, list[str]]] = {c: {k: [] for k in KINDS} for c in CONTEXTS}
    verified = 0
    for context in CONTEXTS:
        for kind in KINDS:
            for phase in range(17):
                key = f"{context}/{phase:02d}/{kind}"
                receipt = godot["captures"].get(key)
                _require(receipt is not None, f"missing receipt {key}")
                path = root / f"flutter-{phase:02d}-{kind}-{context}.png"
                _require(path.exists(), f"missing PNG {path.name}")
                _require(_sha(path) == receipt.get("capture_sha256"), f"capture hash mismatch {path.name}")
                images[context][kind].append(_data_uri(path))
                verified += 1

    seam = {}
    for context in CONTEXTS:
        baseline_equal = godot["captures"][f"{context}/00/baseline"]["capture_sha256"] == godot["captures"][f"{context}/16/baseline"]["capture_sha256"]
        flutter_equal = godot["captures"][f"{context}/00/flutter"]["capture_sha256"] == godot["captures"][f"{context}/16/flutter"]["capture_sha256"]
        neutral_delta = godot["neutral_return"][context]["changed_pixels"]
        _require(baseline_equal and flutter_equal and neutral_delta == 0, f"neutral seam drifted in {context}")
        seam[context] = {"baseline_phase_00_equals_16": baseline_equal, "flutter_phase_00_equals_16": flutter_equal, "changed_pixels": neutral_delta}

    positive_counts = []
    negative_counts = []
    zero_counts = []
    mean_twists = []
    for sample in source["samples"][1:-1]:
        twists = [float(row["twist_deg"]) for row in sample["leaf_records"]]
        positive_counts.append(sum(v > EPS for v in twists))
        negative_counts.append(sum(v < -EPS for v in twists))
        zero_counts.append(sum(abs(v) <= EPS for v in twists))
        mean_twists.append(sum(twists) / len(twists))
    min_pos = min(positive_counts)
    min_neg = min(negative_counts)
    max_zero = max(zero_counts)
    max_abs_mean = max(abs(v) for v in mean_twists)
    _require(min_pos >= 1 and min_neg >= 1, "interior flutter lost opposing leaf twist directions")

    step_s = float(source["effect"]["phase_step_s"])
    duration_s = float(source["effect"]["duration_s"])
    loop_frames = 16  # phase 16 is exact duplicate endpoint witness, not a repeated dwell frame.

    review_summary = {
        "schema": "axm.nature-leaf-flutter-sampled-review/v0.1",
        "state": STATE_REVIEW,
        "vfx_head": head,
        "source_state": source["state"],
        "godot_state": godot["state"],
        "phase_count": 17,
        "displayed_unique_phase_count_per_loop": loop_frames,
        "endpoint_witness_phase": 16,
        "source_phase_step_s": step_s,
        "source_response_duration_s": duration_s,
        "capture_hashes_verified": verified,
        "contexts": list(CONTEXTS),
        "neutral_endpoint_seam": seam,
        "interior_twist_direction_balance": {
            "min_positive_twist_leaves": min_pos,
            "min_negative_twist_leaves": min_neg,
            "max_zero_twist_leaves": max_zero,
            "max_abs_mean_twist_deg": max_abs_mean,
            "note": "diagnostic only; opposing twist signs do not establish natural wind",
        },
        "review_surface": {
            "file": "leaf-flutter-sampled-review.html",
            "self_contained": True,
            "uses_exact_retained_godot_pngs": True,
            "baseline_and_flutter_side_by_side": True,
            "two_fixed_cameras": True,
            "play_pause_scrub_step": True,
            "default_nominal_source_cadence_hz": 1.0 / step_s,
            "playback_excludes_duplicate_endpoint_from_loop": True,
        },
        "truth_boundary": {
            "effect_or_source_reauthored": False,
            "real_godot_frames_reused_exactly": True,
            "browser_playback_is_review_ui_only": True,
            "wall_clock_frame_pacing_proven": False,
            "continuous_interpolation_proven": False,
            "perceptual_naturalness_or_aesthetic_acceptance": False,
            "physical_wind_or_biomechanics": False,
            "gameplay_or_collision": False,
            "target_device_performance": False,
            "current_world_map_receiving_equivalence": False,
            "final_art_or_canon": False,
        },
    }
    summary_path = root / "leaf-flutter-sampled-review-summary.json"
    summary_path.write_text(json.dumps(review_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    payload = json.dumps(images, separators=(",", ":"))
    html = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>AXM Nature leaf flutter — sampled review</title>
<style>
:root{{font-family:system-ui,sans-serif;color-scheme:dark;background:#111;color:#eee}} body{{margin:0;padding:20px;max-width:1500px;margin-inline:auto}} h1{{font-size:1.4rem}} .note{{background:#1c1c1c;padding:12px;border-radius:8px;line-height:1.45}} .controls{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:16px 0}} button,select,input{{font:inherit}} input[type=range]{{width:min(600px,80vw)}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} .panel{{background:#191919;padding:10px;border-radius:8px}} .pair{{display:grid;grid-template-columns:1fr 1fr;gap:8px}} img{{width:100%;height:auto;background:#000}} .label{{font-size:.85rem;opacity:.8;margin:4px 0}} code{{font-family:ui-monospace,monospace}} @media(max-width:900px){{.grid,.pair{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>AXM Nature — bounded leaf-flutter sampled review</h1>
<div class=\"note\"><strong>Review boundary:</strong> these are the exact retained Godot 4.7.2 PNGs from VFX head <code>{head}</code>. The controls only sequence already-captured discrete source phases. Browser timing is <strong>not</strong> wall-clock/performance evidence, there is no interpolation, and this packet does not establish natural wind, physics, gameplay, final art, Map receiving equivalence, or target-device performance. Phase 16 is an exact neutral endpoint witness equal to phase 0 and is excluded from the repeating loop to avoid a duplicate-neutral dwell.</div>
<div class=\"controls\"><button id=\"play\">Play</button><button id=\"prev\">◀</button><button id=\"next\">▶</button><label>Phase <span id=\"phaseText\">00</span>/16 <input id=\"phase\" type=\"range\" min=\"0\" max=\"16\" value=\"0\"></label><label>Review speed <select id=\"speed\"><option value=\"0.25\">0.25×</option><option value=\"0.5\">0.5×</option><option value=\"1\" selected>1× nominal source spacing</option><option value=\"2\">2×</option></select></label></div>
<div class=\"grid\">
<div class=\"panel\"><h2>Ground oblique</h2><div class=\"pair\"><div><div class=\"label\">No-flutter baseline</div><img id=\"ground_base\"></div><div><div class=\"label\">Leaf flutter candidate</div><img id=\"ground_flutter\"></div></div></div>
<div class=\"panel\"><h2>Crown overhead</h2><div class=\"pair\"><div><div class=\"label\">No-flutter baseline</div><img id=\"crown_base\"></div><div><div class=\"label\">Leaf flutter candidate</div><img id=\"crown_flutter\"></div></div></div>
</div>
<script>
const IMAGES={payload}; const STEP_MS={step_s*1000:.12g}; const LOOP_FRAMES=16;
let phase=0, timer=null;
const slider=document.getElementById('phase'), phaseText=document.getElementById('phaseText'), play=document.getElementById('play'), speed=document.getElementById('speed');
function render(){{ phaseText.textContent=String(phase).padStart(2,'0'); slider.value=phase; document.getElementById('ground_base').src=IMAGES.ground_oblique.baseline[phase]; document.getElementById('ground_flutter').src=IMAGES.ground_oblique.flutter[phase]; document.getElementById('crown_base').src=IMAGES.crown_overhead.baseline[phase]; document.getElementById('crown_flutter').src=IMAGES.crown_overhead.flutter[phase]; }}
function stop(){{if(timer!==null){{clearInterval(timer);timer=null;}} play.textContent='Play';}}
function start(){{stop(); if(phase===16) phase=0; render(); play.textContent='Pause'; const ms=STEP_MS/Number(speed.value); timer=setInterval(()=>{{phase=(phase+1)%LOOP_FRAMES;render();}},ms);}}
play.onclick=()=>timer===null?start():stop(); document.getElementById('prev').onclick=()=>{{stop();phase=(phase+16)%17;render();}}; document.getElementById('next').onclick=()=>{{stop();phase=(phase+1)%17;render();}}; slider.oninput=()=>{{stop();phase=Number(slider.value);render();}}; speed.onchange=()=>{{if(timer!==null)start();}}; render();
</script></body></html>"""
    (root / "leaf-flutter-sampled-review.html").write_text(html, encoding="utf-8")
    print(json.dumps({
        "state": STATE_REVIEW,
        "vfx_head": head,
        "capture_hashes_verified": verified,
        "min_positive_twist_leaves": min_pos,
        "min_negative_twist_leaves": min_neg,
        "max_abs_mean_twist_deg": max_abs_mean,
        "html_bytes": len(html.encode('utf-8')),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
