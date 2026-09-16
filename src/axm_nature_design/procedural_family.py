"""Bounded deterministic procedural variation for the first Nature sapling.

This module deliberately varies only already-authored branch/crown degrees of freedom.
It does not generate species, rewrite trunk/flex semantics, or promote one source study
into a universal vegetation system.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import random
from pathlib import Path

from .organic_form import build_evidence, build_mesh, digest, validate_source

FAMILY_SCHEMA = "axm.nature-sapling-variation-family/v0.1"
RECEIPT_SCHEMA = "axm.nature-sapling-variation-receipt/v0.1"

_ALLOWED_BOUNDS = {
    "branch_length_scale",
    "branch_yaw_jitter_deg",
    "leaf_length_scale",
    "leaf_width_scale",
    "leaf_yaw_jitter_deg",
    "leaf_pitch_jitter_deg",
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def family_digest(family: dict) -> str:
    return hashlib.sha256(_canonical_bytes(family)).hexdigest()


def load_family(path: str | Path) -> dict:
    family = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_family(family)
    return family


def _range_pair(value, name: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{name} must be a two-value range")
    lo, hi = float(value[0]), float(value[1])
    if not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
        raise ValueError(f"invalid {name} range")
    return lo, hi


def validate_family(family: dict) -> None:
    if family.get("schema") != FAMILY_SCHEMA:
        raise ValueError("unsupported family schema")
    if not family.get("family_id"):
        raise ValueError("family_id required")
    base = family.get("base_source", {})
    if not base.get("study_id") or not base.get("expected_digest"):
        raise ValueError("base_source study_id and expected_digest required")
    bounds = family.get("bounds", {})
    if set(bounds) != _ALLOWED_BOUNDS:
        raise ValueError("family bounds must use only the declared v0.1 mutation contract")
    for name, value in bounds.items():
        _range_pair(value, name)
    if _range_pair(bounds["branch_length_scale"], "branch_length_scale")[0] <= 0:
        raise ValueError("branch length scale must stay positive")
    if _range_pair(bounds["leaf_length_scale"], "leaf_length_scale")[0] <= 0:
        raise ValueError("leaf length scale must stay positive")
    if _range_pair(bounds["leaf_width_scale"], "leaf_width_scale")[0] <= 0:
        raise ValueError("leaf width scale must stay positive")
    attempts = int(family.get("attempt_limit", 0))
    if attempts < 1 or attempts > 64:
        raise ValueError("attempt_limit must be within 1..64")
    acceptance = family.get("acceptance", {})
    envelope = acceptance.get("max_envelope_m")
    if not isinstance(envelope, list) or len(envelope) != 3 or any(float(v) <= 0 for v in envelope):
        raise ValueError("acceptance.max_envelope_m must contain three positive values")
    if int(acceptance.get("minimum_moved_branch_tips", 0)) < 1:
        raise ValueError("minimum_moved_branch_tips must be positive")
    if float(acceptance.get("minimum_branch_tip_move_m", 0.0)) <= 0:
        raise ValueError("minimum_branch_tip_move_m must be positive")
    if int(acceptance.get("minimum_changed_leaf_blades", 0)) < 1:
        raise ValueError("minimum_changed_leaf_blades must be positive")
    if float(acceptance.get("minimum_leaf_angle_change_deg", 0.0)) <= 0:
        raise ValueError("minimum_leaf_angle_change_deg must be positive")
    seeds = family.get("evidence_seeds", [])
    if len(seeds) < 3 or len(set(int(s) for s in seeds)) != len(seeds):
        raise ValueError("at least three distinct evidence_seeds required")


def _stable_rng(family_hash: str, seed: int, attempt: int) -> random.Random:
    material = f"{family_hash}:{int(seed)}:{int(attempt)}".encode("utf-8")
    state = int.from_bytes(hashlib.sha256(material).digest()[:16], "big")
    return random.Random(state)


def _sample(rng: random.Random, pair) -> float:
    lo, hi = float(pair[0]), float(pair[1])
    return rng.uniform(lo, hi)


def _rotate_xy(dx: float, dy: float, degrees: float) -> tuple[float, float]:
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    return dx * c - dy * s, dx * s + dy * c


def _distance(a, b) -> float:
    return math.sqrt(sum((float(a[i]) - float(b[i])) ** 2 for i in range(3)))


def _branch_cluster_id(branch_id: str) -> str:
    return f"{branch_id}-leaves"


def derive_candidate(base_source: dict, family: dict, seed: int, attempt: int = 0) -> dict:
    """Derive one candidate without changing source-owned trunk/flex/handoff semantics."""
    validate_source(base_source)
    validate_family(family)
    base_hash = digest(base_source)
    expected = family["base_source"]
    if base_source.get("study_id") != expected["study_id"] or base_hash != expected["expected_digest"]:
        raise ValueError("base source identity does not match family contract")

    candidate = copy.deepcopy(base_source)
    fam_hash = family_digest(family)
    rng = _stable_rng(fam_hash, int(seed), int(attempt))
    bounds = family["bounds"]

    varied_tip_by_cluster: dict[str, list[float]] = {}
    branch_variation = []
    for branch in candidate["branches"]:
        original = next(item for item in base_source["branches"] if item["id"] == branch["id"])
        attach = [float(v) for v in original["points"][0]]
        scale = _sample(rng, bounds["branch_length_scale"])
        yaw = _sample(rng, bounds["branch_yaw_jitter_deg"])
        new_points = [list(attach)]
        for point in original["points"][1:]:
            dx = (float(point[0]) - attach[0]) * scale
            dy = (float(point[1]) - attach[1]) * scale
            dz = (float(point[2]) - attach[2]) * scale
            rx, ry = _rotate_xy(dx, dy, yaw)
            new_points.append([attach[0] + rx, attach[1] + ry, attach[2] + dz])
        branch["points"] = new_points
        varied_tip_by_cluster[_branch_cluster_id(branch["id"])] = list(new_points[-1])
        branch_variation.append({
            "branch_id": branch["id"],
            "length_scale": scale,
            "yaw_delta_deg": yaw,
            "tip_move_m": _distance(original["points"][-1], new_points[-1]),
        })

    leaf_variation = []
    base_clusters = {item["id"]: item for item in base_source["leaf_clusters"]}
    for cluster in candidate["leaf_clusters"]:
        original = base_clusters[cluster["id"]]
        if cluster["id"] in varied_tip_by_cluster:
            cluster["center"] = list(varied_tip_by_cluster[cluster["id"]])
        length_scale = _sample(rng, bounds["leaf_length_scale"])
        width_scale = _sample(rng, bounds["leaf_width_scale"])
        cluster["length"] = float(original["length"]) * length_scale
        cluster["width"] = float(original["width"]) * width_scale
        blades = []
        changed = 0
        max_angle_delta = 0.0
        for yaw, pitch in original["blades"]:
            yaw_delta = _sample(rng, bounds["leaf_yaw_jitter_deg"])
            pitch_delta = _sample(rng, bounds["leaf_pitch_jitter_deg"])
            blades.append([float(yaw) + yaw_delta, float(pitch) + pitch_delta])
            delta = max(abs(yaw_delta), abs(pitch_delta))
            max_angle_delta = max(max_angle_delta, delta)
            if delta >= float(family["acceptance"]["minimum_leaf_angle_change_deg"]):
                changed += 1
        cluster["blades"] = blades
        leaf_variation.append({
            "cluster_id": cluster["id"],
            "length_scale": length_scale,
            "width_scale": width_scale,
            "changed_blades": changed,
            "max_angle_delta_deg": max_angle_delta,
        })

    candidate["study_id"] = f"{base_source['study_id']}-variant-{int(seed)}-{int(attempt):02d}"
    candidate["procedural_provenance"] = {
        "family_schema": FAMILY_SCHEMA,
        "family_id": family["family_id"],
        "family_digest": fam_hash,
        "base_source_digest": base_hash,
        "seed": int(seed),
        "attempt": int(attempt),
        "relation": "DERIVED_VARIANT_NOT_SOURCE_REPLACEMENT",
        "branch_variation": branch_variation,
        "leaf_variation": leaf_variation,
    }
    candidate["truth_boundary"] = (
        base_source["truth_boundary"]
        + " This derived variant additionally does not establish species variation, biological growth, "
          "environment acceptance, deformation, runtime readiness, or a universal vegetation generator."
    )
    return candidate


def variation_metrics(base_source: dict, candidate: dict, family: dict) -> dict:
    base_branches = {item["id"]: item for item in base_source["branches"]}
    moved = []
    for branch in candidate["branches"]:
        move = _distance(base_branches[branch["id"]]["points"][-1], branch["points"][-1])
        moved.append({"branch_id": branch["id"], "tip_move_m": move})
    threshold = float(family["acceptance"]["minimum_branch_tip_move_m"])
    moved_count = sum(item["tip_move_m"] >= threshold for item in moved)

    base_clusters = {item["id"]: item for item in base_source["leaf_clusters"]}
    leaf_changes = []
    leaf_threshold = float(family["acceptance"]["minimum_leaf_angle_change_deg"])
    changed_leaf_count = 0
    for cluster in candidate["leaf_clusters"]:
        original = base_clusters[cluster["id"]]
        for idx, ((yaw0, pitch0), (yaw1, pitch1)) in enumerate(zip(original["blades"], cluster["blades"])):
            delta = max(abs(float(yaw1) - float(yaw0)), abs(float(pitch1) - float(pitch0)))
            leaf_changes.append({"cluster_id": cluster["id"], "blade": idx, "angle_delta_deg": delta})
            if delta >= leaf_threshold:
                changed_leaf_count += 1

    mesh = build_mesh(candidate)
    evidence = build_evidence(candidate)
    size = [float(v) for v in evidence["design"]["bounds_m"]["size"]]
    envelope = [float(v) for v in family["acceptance"]["max_envelope_m"]]
    envelope_ok = all(size[i] <= envelope[i] + 1e-12 for i in range(3))
    attachments_preserved = all(
        branch["points"][0] == base_branches[branch["id"]]["points"][0]
        for branch in candidate["branches"]
    )
    immutable_fields_preserved = all(
        candidate[key] == base_source[key]
        for key in ("trunk", "flex_zones", "design_checks", "donor_provenance", "environment_handoff", "weather_handoff")
    )
    return {
        "branch_tip_moves": moved,
        "moved_branch_tips": moved_count,
        "changed_leaf_blades": changed_leaf_count,
        "leaf_changes": leaf_changes,
        "mesh_digest": digest(mesh),
        "source_digest": digest(candidate),
        "bounds_m": evidence["design"]["bounds_m"],
        "organic_evidence_state": evidence["state"],
        "organic_checks_pass": bool(evidence["structural"]["pass"] and evidence["design"]["pass"]),
        "envelope_ok": envelope_ok,
        "attachments_preserved": attachments_preserved,
        "immutable_fields_preserved": immutable_fields_preserved,
    }


def _passes(metrics: dict, family: dict) -> bool:
    acceptance = family["acceptance"]
    return all((
        metrics["organic_checks_pass"],
        metrics["envelope_ok"],
        metrics["attachments_preserved"],
        metrics["immutable_fields_preserved"],
        metrics["moved_branch_tips"] >= int(acceptance["minimum_moved_branch_tips"]),
        metrics["changed_leaf_blades"] >= int(acceptance["minimum_changed_leaf_blades"]),
    ))


def generate_accepted_variant(base_source: dict, family: dict, seed: int) -> dict:
    """Bounded rejection search. Failure returns HOLD rather than widening authored bounds."""
    validate_source(base_source)
    validate_family(family)
    fam_hash = family_digest(family)
    base_hash = digest(base_source)
    attempts = int(family["attempt_limit"])
    rejected = []
    for attempt in range(attempts):
        candidate = derive_candidate(base_source, family, int(seed), attempt)
        metrics = variation_metrics(base_source, candidate, family)
        if _passes(metrics, family):
            receipt = {
                "schema": RECEIPT_SCHEMA,
                "state": "PASS_BOUNDED_VARIANT",
                "family_id": family["family_id"],
                "family_digest": fam_hash,
                "base_source_digest": base_hash,
                "seed": int(seed),
                "accepted_attempt": attempt,
                "candidate_source_digest": metrics["source_digest"],
                "candidate_mesh_digest": metrics["mesh_digest"],
                "metrics": metrics,
                "rejected_attempts_before_acceptance": rejected,
                "truth_boundary": family["truth_boundary"],
            }
            return {"candidate": candidate, "receipt": receipt}
        rejected.append({
            "attempt": attempt,
            "organic_checks_pass": metrics["organic_checks_pass"],
            "envelope_ok": metrics["envelope_ok"],
            "moved_branch_tips": metrics["moved_branch_tips"],
            "changed_leaf_blades": metrics["changed_leaf_blades"],
        })
    return {
        "candidate": None,
        "receipt": {
            "schema": RECEIPT_SCHEMA,
            "state": "HOLD_NO_VALID_VARIANT",
            "family_id": family["family_id"],
            "family_digest": fam_hash,
            "base_source_digest": base_hash,
            "seed": int(seed),
            "attempt_limit": attempts,
            "rejected_attempts": rejected,
            "truth_boundary": family["truth_boundary"],
        },
    }
