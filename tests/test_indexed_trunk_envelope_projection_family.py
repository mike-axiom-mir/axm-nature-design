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

from axm_nature_design.indexed_trunk_envelope_projection_family import (
    PREDECESSOR_SCHEMA,
    RELATION,
    SCHEMA,
    assemble_indexed_trunk_envelope_projection_family,
    digest,
    project_point_to_regular_tapered_shell,
    validate_contract,
)
from axm_nature_design.trunk_envelope_projection_family import project_point_to_tapered_trunk


class IndexedTrunkEnvelopeProjectionFamilyTests(unittest.TestCase):
    def setUp(self):
        self.branch_ids = ["south-low", "north-low", "east-mid", "west-high", "north-top"]
        self.source = {
            "trunk": [
                {"id": "low", "position": [0.0, 0.0, 0.0], "radius": 1.0},
                {"id": "high", "position": [0.0, 0.0, 10.0], "radius": 0.5},
            ]
        }
        outputs = []
        for index, branch_id in enumerate(self.branch_ids):
            z = 1.0 + index * 1.5
            t = z / 10.0
            radius = 1.0 + t * (0.5 - 1.0)
            branch_radius = 0.10 + 0.01 * index
            angle = 0.19 + 0.41 * index
            # Vertical-segment frame is u=+Y, v=-X.
            radial = [-math.sin(angle), math.cos(angle), 0.0]
            azimuth = [-math.cos(angle), -math.sin(angle), 0.0]
            center = [
                radial[0] * (radius + branch_radius),
                radial[1] * (radius + branch_radius),
                z,
            ]
            points = [
                center,
                [center[i] + branch_radius * azimuth[i] for i in range(3)],
                [center[i] - branch_radius * azimuth[i] for i in range(3)],
            ]
            samples = [project_point_to_tapered_trunk(self.source, "low->high", point) for point in points]
            core = {
                "output_id": f"{branch_id}-transition-trunk-envelope-projection",
                "branch_id": branch_id,
                "trunk_segment_id": "low->high",
                "sample_semantics": [
                    "exit-center",
                    "exit-center-plus-azimuth-radius",
                    "exit-center-minus-azimuth-radius",
                ],
                "samples": samples,
                "downstream_adoption_authorized": False,
            }
            outputs.append({**core, "projection_digest": digest(core)})
        predecessor_core = {
            "schema": PREDECESSOR_SCHEMA,
            "family_id": "smooth-fixture",
            "outputs": sorted(outputs, key=lambda row: row["branch_id"]),
        }
        self.predecessor = {**predecessor_core, "family_digest": digest(predecessor_core)}
        self.contract = {
            "schema": SCHEMA,
            "family_id": "indexed-fixture",
            "relation": RELATION,
            "predecessor_projection_family_schema": PREDECESSOR_SCHEMA,
            "predecessor_projection_family_digest": self.predecessor["family_digest"],
            "organic_source_digest": digest(self.source),
            "authorized_branch_ids": list(self.branch_ids),
            "receiver_side_count": 10,
            "receiver_phase_rad": 0.0,
            "predecessor_projection": {
                "module_path": "src/fixture.py",
                "module_blob": "1" * 40,
                "contract_path": "examples/fixture.json",
                "contract_blob": "2" * 40,
                "frame_contract_path": "examples/frame-fixture.json",
                "frame_contract_blob": "5" * 40,
            },
            "geometry_reference": {
                "repository": "mike-axiom-mir/axm-nature-design",
                "head": "3" * 40,
                "module_path": "src/geometry_fixture.py",
                "module_blob": "4" * 40,
                "branch_id": "north-low",
                "side_count": 10,
                "phase_rad": 0.0,
            },
            "source_mutation_authorized": False,
            "triangle_membership_authorized": False,
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

    def test_regular_polygon_mid_side_projection(self):
        point = [-math.sqrt(2.0), math.sqrt(2.0), 5.0]
        row = project_point_to_regular_tapered_shell(
            self.source, "low->high", point, side_count=4, phase_rad=0.0
        )
        self.assertAlmostEqual(0.5, row["segment_t"])
        self.assertAlmostEqual(0.75, row["local_radius_m"])
        self.assertAlmostEqual(0.75 / math.sqrt(2.0), row["indexed_radial_distance_m"])
        self.assertAlmostEqual(0.5, row["side_edge_lambda"])
        self.assertEqual(0, row["side_cell"])
        self.assertAlmostEqual(0.0, row["surface_edge_residual_m"])
        self.assertAlmostEqual(0.0, row["axial_coordinate_residual_m"])

    def test_five_materially_different_outputs(self):
        family = assemble_indexed_trunk_envelope_projection_family(
            self.source, self.predecessor, self.contract
        )
        self.assertEqual(5, family["output_count"])
        self.assertEqual(5, len({row["projection_digest"] for row in family["outputs"]}))
        self.assertGreater(family["maximum_analytic_to_indexed_surface_delta_m"], 1e-10)
        self.assertFalse(family["geometry_triangle_membership_authority"])
        self.assertFalse(family["geometry_ring_topology_authority"])
        self.assertFalse(family["connected_junction_authority"])
        self.assertFalse(family["rigging_authority"])

    def test_input_order_does_not_change_family_identity(self):
        forward = assemble_indexed_trunk_envelope_projection_family(
            self.source, self.predecessor, self.contract
        )
        predecessor = copy.deepcopy(self.predecessor)
        predecessor["outputs"] = list(reversed(predecessor["outputs"]))
        contract = copy.deepcopy(self.contract)
        contract["authorized_branch_ids"] = list(reversed(contract["authorized_branch_ids"]))
        reverse = assemble_indexed_trunk_envelope_projection_family(
            self.source, predecessor, contract
        )
        self.assertEqual(forward["family_digest"], reverse["family_digest"])

    def test_phase_changes_projection_without_changing_axial_coordinate(self):
        point = [-1.2, 1.5, 5.0]
        zero = project_point_to_regular_tapered_shell(
            self.source, "low->high", point, side_count=10, phase_rad=0.0
        )
        shifted = project_point_to_regular_tapered_shell(
            self.source, "low->high", point, side_count=10, phase_rad=math.pi / 10.0
        )
        self.assertAlmostEqual(zero["segment_t"], shifted["segment_t"])
        self.assertAlmostEqual(zero["local_radius_m"], shifted["local_radius_m"])
        self.assertNotAlmostEqual(
            zero["indexed_radial_distance_m"], shifted["indexed_radial_distance_m"], places=8
        )

    def test_centerline_and_outside_segment_fail_closed(self):
        with self.assertRaises(ValueError):
            project_point_to_regular_tapered_shell(
                self.source, "low->high", [0.0, 0.0, 5.0], side_count=10
            )
        with self.assertRaises(ValueError):
            project_point_to_regular_tapered_shell(
                self.source, "low->high", [1.0, 0.0, 11.0], side_count=10
            )

    def test_invalid_side_count_fails_closed(self):
        for side_count in (0, 2, True, 3.5):
            with self.subTest(side_count=side_count):
                with self.assertRaises(ValueError):
                    project_point_to_regular_tapered_shell(
                        self.source, "low->high", [1.0, 0.0, 5.0], side_count=side_count
                    )

    def test_predecessor_digest_drift_fails_closed(self):
        predecessor = copy.deepcopy(self.predecessor)
        predecessor["family_digest"] = "0" * 64
        with self.assertRaises(ValueError):
            assemble_indexed_trunk_envelope_projection_family(
                self.source, predecessor, self.contract
            )

    def test_receiver_side_count_and_phase_pins_fail_closed(self):
        side = copy.deepcopy(self.contract)
        side["receiver_side_count"] = 12
        with self.assertRaises(ValueError):
            validate_contract(side)
        phase = copy.deepcopy(self.contract)
        phase["receiver_phase_rad"] = 0.1
        with self.assertRaises(ValueError):
            validate_contract(phase)

    def test_authority_promotions_fail_closed(self):
        for key in (
            "triangle_membership_authorized",
            "ring_topology_authorized",
            "indexed_trunk_cut_authorized",
            "connected_junction_authorized",
            "weld_or_remesh_authorized",
            "automatic_rigging_adoption",
            "automatic_runtime_adoption",
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
