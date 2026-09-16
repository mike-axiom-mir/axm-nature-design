"""Deterministic source-owned organic vegetation form study.

The first candidate is intentionally a stylized sapling. It retains explicit source
points, taper and declared flex zones while keeping rig/deformation/weather/runtime
claims outside this module.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

SCHEMA = "axm.nature-organic-form-study/v0.1"
EVIDENCE_SCHEMA = "axm.nature-organic-form-evidence/v0.1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _add(a, b): return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]
def _sub(a, b): return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]
def _mul(a, s): return [a[0]*s, a[1]*s, a[2]*s]
def _dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def _cross(a, b): return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def _length(v): return math.sqrt(_dot(v, v))


def _norm(v):
    n = _length(v)
    if n <= 1e-12:
        raise ValueError("zero-length direction")
    return [v[0]/n, v[1]/n, v[2]/n]


def _frame(a, b):
    axis = _norm(_sub(b, a))
    ref = [0.0, 0.0, 1.0]
    if abs(_dot(axis, ref)) > 0.94:
        ref = [1.0, 0.0, 0.0]
    u = _norm(_cross(axis, ref))
    v = _norm(_cross(axis, u))
    return axis, u, v


def _empty_mesh():
    return {"schema": "axm.nature-triangle-mesh/v0.1", "vertices": [], "triangles": [], "regions": []}


def _add_tapered_segment(mesh, region_id, a, b, r0, r1, sides=8):
    if r0 <= 0 or r1 <= 0:
        raise ValueError("radii must be positive")
    _, u, v = _frame(a, b)
    start = len(mesh["vertices"])
    for point, radius in ((a, r0), (b, r1)):
        for i in range(sides):
            angle = math.tau * i / sides
            radial = _add(_mul(u, math.cos(angle)*radius), _mul(v, math.sin(angle)*radius))
            mesh["vertices"].append(_add(point, radial))
    c0 = len(mesh["vertices"]); mesh["vertices"].append(list(a))
    c1 = len(mesh["vertices"]); mesh["vertices"].append(list(b))
    tri_start = len(mesh["triangles"])
    for i in range(sides):
        j = (i + 1) % sides
        a0, a1, b0, b1 = start+i, start+j, start+sides+i, start+sides+j
        # Source-lineage migration: cap perimeter traversal must oppose adjacent side faces.
        mesh["triangles"].extend([[a0,b0,b1],[a0,b1,a1],[c0,a0,a1],[c1,b1,b0]])
    mesh["regions"].append({"id": region_id, "triangle_start": tri_start, "triangle_count": sides*4, "kind": "tapered-segment"})


def _leaf_direction(yaw_deg, pitch_deg):
    yaw = math.radians(yaw_deg); pitch = math.radians(pitch_deg)
    horizontal = math.cos(pitch)
    return [horizontal*math.cos(yaw), horizontal*math.sin(yaw), math.sin(pitch)]


def _add_leaf_blade(mesh, region_id, center, length, width, yaw_deg, pitch_deg):
    """Add an independently authored lozenge blade.

    Donor discovery identified a useful idea in UC's small RTS vegetation: a
    stem plus cheap planar leaf blades. This receiving implementation is not a
    copy of the donor function; it uses explicit blade parameters and is tested
    independently here.
    """
    forward = _norm(_leaf_direction(yaw_deg, pitch_deg))
    up = [0.0, 0.0, 1.0]
    side = _cross(forward, up)
    if _length(side) < 1e-7:
        side = [1.0, 0.0, 0.0]
    side = _norm(side)
    base = list(center)
    tip = _add(base, _mul(forward, length))
    mid = _mul(_add(base, tip), 0.5)
    left = _add(mid, _mul(side, width*0.5))
    right = _sub(mid, _mul(side, width*0.5))
    start = len(mesh["vertices"])
    mesh["vertices"].extend([base, left, tip, right])
    tri_start = len(mesh["triangles"])
    mesh["triangles"].extend([[start,start+1,start+2],[start,start+2,start+3]])
    mesh["regions"].append({"id": region_id, "triangle_start": tri_start, "triangle_count": 2, "kind": "leaf-blade"})


def load_source(path: str | Path) -> dict:
    source = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_source(source)
    return source


def validate_source(source: dict) -> None:
    if source.get("schema") != SCHEMA:
        raise ValueError("unsupported source schema")
    trunk = source.get("trunk", [])
    if len(trunk) < 3:
        raise ValueError("trunk requires at least three points")
    radii = [float(p["radius"]) for p in trunk]
    if any(r <= 0 for r in radii):
        raise ValueError("trunk radii must be positive")
    branches = source.get("branches", [])
    for branch in branches:
        if len(branch.get("points", [])) != len(branch.get("radii", [])) or len(branch.get("points", [])) < 2:
            raise ValueError(f"invalid branch {branch.get('id')}")
    for zone in source.get("flex_zones", []):
        if zone.get("status") != "DECLARED_NOT_DEFORMATION_TESTED":
            raise ValueError("flex zones may not silently claim deformation evidence")
    donor = source.get("donor_provenance", {})
    required = {"repository", "commit", "path", "license", "evidence_relation"}
    if not required.issubset(donor):
        raise ValueError("donor provenance incomplete")


def build_mesh(source: dict) -> dict:
    validate_source(source)
    mesh = _empty_mesh()
    trunk = source["trunk"]
    for i in range(len(trunk)-1):
        _add_tapered_segment(mesh, f"trunk:{trunk[i]['id']}->{trunk[i+1]['id']}", trunk[i]["position"], trunk[i+1]["position"], float(trunk[i]["radius"]), float(trunk[i+1]["radius"]), sides=10)
    for branch in source["branches"]:
        points, radii = branch["points"], branch["radii"]
        for i in range(len(points)-1):
            _add_tapered_segment(mesh, f"branch:{branch['id']}:{i}", points[i], points[i+1], float(radii[i]), float(radii[i+1]), sides=8)
    for cluster in source["leaf_clusters"]:
        for i, (yaw, pitch) in enumerate(cluster["blades"]):
            _add_leaf_blade(mesh, f"leaf:{cluster['id']}:{i}", cluster["center"], float(cluster["length"]), float(cluster["width"]), float(yaw), float(pitch))
    return mesh


def _bounds(vertices: Iterable[Iterable[float]]):
    verts = [list(v) for v in vertices]
    mins = [min(v[i] for v in verts) for i in range(3)]
    maxs = [max(v[i] for v in verts) for i in range(3)]
    return {"min": mins, "max": maxs, "size": [maxs[i]-mins[i] for i in range(3)]}


def _triangle_area(a, b, c):
    return 0.5 * _length(_cross(_sub(b,a), _sub(c,a)))


def structural_checks(mesh: dict) -> dict:
    vertices, triangles = mesh["vertices"], mesh["triangles"]
    finite = all(math.isfinite(float(x)) for v in vertices for x in v)
    bounded = all(len(t)==3 and all(isinstance(i, int) and 0 <= i < len(vertices) for i in t) for t in triangles)
    degenerate = 0
    if bounded:
        for t in triangles:
            if _triangle_area(vertices[t[0]], vertices[t[1]], vertices[t[2]]) <= 1e-10:
                degenerate += 1
    return {"finite_vertices": finite, "bounded_indices": bounded, "degenerate_triangles": degenerate, "pass": finite and bounded and degenerate == 0}


def design_checks(source: dict, mesh: dict) -> dict:
    bounds = _bounds(mesh["vertices"])
    checks = source["design_checks"]
    radii = [float(p["radius"]) for p in source["trunk"]]
    taper_ok = all(a > b for a,b in zip(radii, radii[1:]))
    branch_tip_heights = [float(b["points"][-1][2]) for b in source["branches"]]
    height = bounds["max"][2] - bounds["min"][2]
    width_x = bounds["size"][0]
    depth_y = bounds["size"][1]
    tests = {
        "height_range": checks["height_m"][0] <= height <= checks["height_m"][1],
        "crown_width_x_range": checks["crown_width_x_m"][0] <= width_x <= checks["crown_width_x_m"][1],
        "crown_depth_y_range": checks["crown_depth_y_m"][0] <= depth_y <= checks["crown_depth_y_m"][1],
        "minimum_branch_tip_height": min(branch_tip_heights) >= checks["minimum_branch_tip_height_m"],
        "trunk_taper_strict": taper_ok,
        "ground_floor": bounds["min"][2] >= checks["ground_min_z_m"],
        "flex_zones_unproven": all(z["status"] == "DECLARED_NOT_DEFORMATION_TESTED" for z in source["flex_zones"]),
        "environment_not_composed": source["environment_handoff"]["status"] == "CANDIDATE_REPLACEMENT_NOT_COMPOSED",
        "weather_not_applied": source["weather_handoff"]["status"] == "CONTEXT_ONLY_NOT_APPLIED_TO_FORM"
    }
    return {"bounds_m": bounds, "measures": {"height_m": height, "width_x_m": width_x, "depth_y_m": depth_y, "minimum_branch_tip_height_m": min(branch_tip_heights)}, "checks": tests, "pass": all(tests.values())}


def build_evidence(source: dict) -> dict:
    mesh = build_mesh(source)
    structural = structural_checks(mesh)
    design = design_checks(source, mesh)
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "study_id": source["study_id"],
        "state": "PASS_AUTHORED_ORGANIC_FORM_INTENT" if structural["pass"] and design["pass"] else "FAIL",
        "source_digest": digest(source),
        "mesh_digest": digest(mesh),
        "vertices": len(mesh["vertices"]),
        "triangles": len(mesh["triangles"]),
        "regions": len(mesh["regions"]),
        "trunk_points": len(source["trunk"]),
        "branches": len(source["branches"]),
        "leaf_blades": sum(len(c["blades"]) for c in source["leaf_clusters"]),
        "flex_zones": [{"id": z["id"], "status": z["status"]} for z in source["flex_zones"]],
        "structural": structural,
        "design": design,
        "donor_provenance": source["donor_provenance"],
        "environment_handoff": source["environment_handoff"],
        "weather_handoff": source["weather_handoff"],
        "truth_boundary": source["truth_boundary"]
    }
    return evidence


def write_obj(mesh: dict, path: str | Path):
    lines = ["# AXM nature organic sapling evidence", "o sapling-neutral-001"]
    for v in mesh["vertices"]:
        lines.append(f"v {v[0]:.9f} {v[1]:.9f} {v[2]:.9f}")
    for t in mesh["triangles"]:
        lines.append(f"f {t[0]+1} {t[1]+1} {t[2]+1}")
    Path(path).write_text("\n".join(lines)+"\n", encoding="utf-8")


def _unique_edges(triangles):
    edges = set()
    for a,b,c in triangles:
        for x,y in ((a,b),(b,c),(c,a)):
            edges.add(tuple(sorted((x,y))))
    return sorted(edges)


def write_svg(mesh: dict, path: str | Path, view: str):
    axes = {"front": (0,2), "side": (1,2), "top": (0,1)}
    if view not in axes:
        raise ValueError("unknown view")
    ax0, ax1 = axes[view]
    pts = [(v[ax0], v[ax1]) for v in mesh["vertices"]]
    min0,max0 = min(p[0] for p in pts), max(p[0] for p in pts)
    min1,max1 = min(p[1] for p in pts), max(p[1] for p in pts)
    span0=max(max0-min0,1e-9); span1=max(max1-min1,1e-9)
    scale=min(520/span0,520/span1)
    ox=300-(min0+max0)*0.5*scale; oy=300+(min1+max1)*0.5*scale
    def p2(p): return (ox+p[0]*scale, oy-p[1]*scale)
    lines=["<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"600\" height=\"600\" viewBox=\"0 0 600 600\">", "<rect width=\"600\" height=\"600\" fill=\"white\"/>", f"<text x=\"20\" y=\"30\" font-family=\"monospace\" font-size=\"18\">sapling-neutral-001 / {view}</text>"]
    for a,b in _unique_edges(mesh["triangles"]):
        x1,y1=p2(pts[a]); x2,y2=p2(pts[b])
        lines.append(f"<line x1=\"{x1:.3f}\" y1=\"{y1:.3f}\" x2=\"{x2:.3f}\" y2=\"{y2:.3f}\" stroke=\"#111\" stroke-width=\"0.7\" stroke-opacity=\"0.58\"/>")
    lines.append("</svg>")
    Path(path).write_text("\n".join(lines)+"\n", encoding="utf-8")
