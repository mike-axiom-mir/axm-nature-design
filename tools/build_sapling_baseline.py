#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from axm_nature_design.organic_form import build_evidence, build_mesh, load_source, write_obj, write_svg

source_path = ROOT / "examples" / "sapling_neutral_001.json"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "evidence" / "sapling-neutral-001"
out.mkdir(parents=True, exist_ok=True)
source = load_source(source_path)
mesh = build_mesh(source)
evidence = build_evidence(source)
(out / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True)+"\n", encoding="utf-8")
(out / "mesh.json").write_text(json.dumps(mesh, indent=2, sort_keys=True)+"\n", encoding="utf-8")
write_obj(mesh, out / "sapling.obj")
for view in ("front", "side", "top"):
    write_svg(mesh, out / f"{view}.svg", view)
print(json.dumps({"state": evidence["state"], "source_digest": evidence["source_digest"], "mesh_digest": evidence["mesh_digest"], "vertices": evidence["vertices"], "triangles": evidence["triangles"], "bounds_m": evidence["design"]["bounds_m"]}, sort_keys=True))
if evidence["state"] != "PASS_AUTHORED_ORGANIC_FORM_INTENT":
    raise SystemExit(1)
