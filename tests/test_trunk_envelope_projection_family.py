from __future__ import annotations

import copy
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from axm_nature_design.trunk_envelope_projection_family import (
    OWNER_FRAME_SCHEMA,
    OWNER_FRAME_STATE,
    PREDECESSOR_FRAME_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_trunk_envelope_projection_family,
    digest,
    project_point_to_tapered_trunk,
    validate_contract,
)


class TrunkEnvelopeProjectionFamilyTests(unittest.TestCase):
    def setUp(self):
        self.branch_ids = ["south-low", "north-low", "east-mid", "west-high", "north-top"]
        self.source = {
            "trunk": [
                {"id": "low", "position": [0.0, 0.0, 0.0], "radius": 1.0},
                {"id": "high", "position": [0.0, 0.0, 10.0], "radius": 0.5},
            ]
        }
        frames = []
        predecessor_outputs = []
        for index, branch_id in enumerate(self.branch_ids):
            z = 1.0 + index * 1.5
            t = z / 10.0
            trunk_radius = 1.0 + t * (0.5 - 1.0)
            branch_radius = 0.10 + 0.01 * index
            angle = 0.35 * index
            radial = [math.cos(angle), math.sin(angle), 0.0]
            azimuth = [-math.sin(angle), math.cos(angle), 0.0]
            center = [
                radial[0] * (trunk_radius + branch_radius),
                radial[1] * (trunk_radius + branch_radius),
                z,
            ]
            frames.append({
                "branch_id": branch_id,
                "exit_center_m": center,
                "exit_branch_radius_m": branch_radius,
                "exit_local_trunk_radius_m": trunk_radius,
                "nearest_trunk_segment": "low->high",
                "nearest_trunk_segment_t": t,
            })
            predecessor_outputs.append({
                "branch_id": branch_id,
                "origin_exit_center_m": center,
                "exit_branch_radius_m": branch_radius,
                "basis": {"y_azimuth_around_trunk_unit": azimuth},
                "downstream_adoption_authorized": False,
            })

        self.owner_report = {
            "schema": OWNER_FRAME_SCHEMA,
            "state": OWNER_FRAME_STATE,
            "frames": frames,
        }
        predecessor_core = {
            "schema": PREDECESSOR_FRAME_SCHEMA,
            "outputs": predecessor_outputs,
        }
        predecessor_digest = digest(predecessor_core)
        self.predecessor = {**predecessor_core, "family_digest": predecessor_digest}
        self.contract = {
            "schema": SCHEMA,
            "family_id": "projection-family-fixture",
            "relation": RELATION,
            "predecessor_frame_family_schema": PREDECESSOR_FRAME_SCHEMA,
            "predecessor_frame_family_digest": predecessor_digest,
            "organic_source_digest": digest(self.source),
            "authorized_branch_ids": list(self.branch_ids),
            "geometry_reference": {
                "head": "1" * 40,
                "module_blob": "2" * 40,
                "module_path": "fixture.py",
                "branch_id": "north-low",
            },
            "source_mutation_authorized": False,
            "ring_topology_authorized": False,
            "bridge_topology_authorized": False,
            "indexed_trunk_cut_authorized": False,
            "connected_junction_authorized": False,
            "weld_or_remesh_authorized": False,
            "surface_normal_authorized": False,
            "automatic_geometry_adoption": False,
            "automatic_rigging_adoption": False,
            "automatic_animation_adoption": False,
            "automatic_vfx_adoption": False,
            "automatic_technical_art_adoption": False,
            "automatic_runtime_adoption": False,
            "production_weight_authorized": False,
        }

    def test_five_materially_different_outputs(self):
        family = assemble_trunk_envelope_projection_family(
            self.source, self.owner_report, self.predecessor, self.contract
        )
        self.assertEqual(5, family["output_count"])
        self.assertEqual(5, len({row["projection_digest"] for row in family["outputs"]}))
        self.assertFalse(family["geometry_ring_topology_authority"])
        self.assertFalse(family["geometry_bridge_topology_authority"])
        self.assertFalse(family["connected_junction_authority"])
        self.assertFalse(family["rigging_authority"])

    def test_projection_preserves_axial_coordinate_and_tapered_radius(self):
        row = project_point_to_tapered_trunk(self.source, "low->high", [2.0, 0.0, 5.0])
        self.assertAlmostEqual(0.5, row["segment_t"])
        self.assertAlmostEqual(0.75, row["local_radius_m"])
        self.assertAlmostEqual(0.0, row["surface_residual_m"])
        self.assertAlmostEqual(0.0, row["axial_coordinate_residual_m"])
        self.assertAlmostEqual(1.25, row["projection_span_m"])

    def test_input_order_does_not_change_family_identity(self):
        forward = assemble_trunk_envelope_projection_family(
            self.source, self.owner_report, self.predecessor, self.contract
        )
        owner = copy.deepcopy(self.owner_report)
        owner["frames"] = list(reversed(owner["frames"]))
        predecessor = copy.deepcopy(self.predecessor)
        predecessor["outputs"] = list(reversed(predecessor["outputs"]))
        contract = copy.deepcopy(self.contract)
        contract["authorized_branch_ids"] = list(reversed(contract["authorized_branch_ids"]))
        reverse = assemble_trunk_envelope_projection_family(self.source, owner, predecessor, contract)
        self.assertEqual(forward["family_digest"], reverse["family_digest"])

    def test_centerline_point_fails_closed(self):
        with self.assertRaises(ValueError):
            project_point_to_tapered_trunk(self.source, "low->high", [0.0, 0.0, 5.0])

    def test_point_outside_segment_fails_closed(self):
        with self.assertRaises(ValueError):
            project_point_to_tapered_trunk(self.source, "low->high", [1.0, 0.0, 11.0])

    def test_predecessor_digest_drift_fails_closed(self):
        predecessor = copy.deepcopy(self.predecessor)
        predecessor["family_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            assemble_trunk_envelope_projection_family(
                self.source, self.owner_report, predecessor, self.contract
            )

    def test_owner_state_drift_fails_closed(self):
        owner = copy.deepcopy(self.owner_report)
        owner["state"] = "HOLD_FRAME_REVIEW"
        with self.assertRaises(ValueError):
            assemble_trunk_envelope_projection_family(self.source, owner, self.predecessor, self.contract)

    def test_authority_promotions_fail_closed(self):
        for key in (
            "ring_topology_authorized",
            "indexed_trunk_cut_authorized",
            "connected_junction_authorized",
            "weld_or_remesh_authorized",
            "automatic_rigging_adoption",
        ):
            contract = copy.deepcopy(self.contract)
            contract[key] = True
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    validate_contract(contract)

    def test_duplicate_branch_declaration_fails_closed(self):
        contract = copy.deepcopy(self.contract)
        contract["authorized_branch_ids"][-1] = contract["authorized_branch_ids"][0]
        with self.assertRaises(ValueError):
            validate_contract(contract)


if __name__ == "__main__":
    unittest.main()
