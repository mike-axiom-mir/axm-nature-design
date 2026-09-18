from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from axm_nature_design.organic_form import load_source, write_obj
from axm_nature_design.wind_response_migrated import (
    MIGRATED_NEUTRAL_MESH_DIGEST,
    build_evidence,
    deform_mesh,
    load_spec,
    write_comparison_svg,
)

SOURCE = ROOT / 'examples' / 'sapling_neutral_001.json'
SPEC = ROOT / 'examples' / 'sapling_wind_response_migrated_001.json'


def main() -> int:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'evidence' / 'sapling-wind-response-migrated-001'
    out.mkdir(parents=True, exist_ok=True)
    source = load_source(SOURCE)
    spec = load_spec(SPEC)
    evidence = build_evidence(source, spec)
    if evidence['state'] != 'PASS_BOUNDED_VISUAL_WIND_RESPONSE':
        raise SystemExit('migrated visual wind response evidence did not pass')
    if evidence['migration_rebind']['migrated_neutral_mesh_digest'] != MIGRATED_NEUTRAL_MESH_DIGEST:
        raise SystemExit('migrated neutral mesh identity drifted')

    (out / 'evidence.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    meshes = []
    for time_s in spec['response']['sample_times_s']:
        mesh = deform_mesh(source, spec, float(time_s))
        meshes.append((float(time_s), mesh))
        millis = int(round(float(time_s) * 1000.0))
        (out / f'frame_{millis:04d}ms_mesh.json').write_text(json.dumps(mesh, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        write_obj(mesh, out / f'frame_{millis:04d}ms.obj')

    for view in ('front', 'side', 'top'):
        write_comparison_svg(meshes, out / f'{view}_comparison.svg', view)

    summary = {
        'state': 'PASS_MIGRATED_TOPOLOGY_VISUAL_WIND_RESPONSE_REBIND',
        'underlying_response_state': evidence['state'],
        'samples': len(evidence['samples']),
        'migrated_neutral_mesh_digest': MIGRATED_NEUTRAL_MESH_DIGEST,
        'peak_max_displacement_m': max(s['max_displacement_m'] for s in evidence['samples']),
        'peak_crosswind_residual_m': max(s['max_abs_crosswind_drift_m'] for s in evidence['samples']),
        'max_anchor_displacement_m': max(s['max_anchor_displacement_m'] for s in evidence['samples']),
        'response_profile_changed': evidence['migration_rebind']['response_profile_changed'],
        'source_json_changed': evidence['migration_rebind']['source_json_changed'],
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
