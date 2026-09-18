import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_transition_exit_frames import evaluate

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeTransitionExitFrameTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def _frames(self, report):
        return {row["branch_id"]: row for row in report["frames"]}

    def test_current_source_has_five_exact_neutral_transition_exit_frames(self):
        report = evaluate(self.source)
        self.assertEqual(
            report["state"],
            "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_EXIT_FRAMES__CONNECTED_TOPOLOGY_HELD",
        )
        self.assertEqual(report["schema"], "axm.nature-neutral-branch-transition-exit-frame/v0.1")
        self.assertEqual(report["branch_count"], 5)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(
            [row["branch_id"] for row in report["frames"]],
            ["south-low", "north-low", "east-mid", "west-high", "north-top"],
        )
        self.assertAlmostEqual(report["minimum_departure_angle_deg"], 44.370330295008024, places=10)
        self.assertAlmostEqual(report["maximum_departure_angle_deg"], 53.27022259196141, places=10)
        self.assertLessEqual(report["maximum_frame_orthogonality_error"], 1e-9)
        self.assertLessEqual(report["maximum_branch_tangent_reconstruction_error"], 1e-9)

    def test_north_low_exit_frame_is_exact_source_form_handoff(self):
        north_low = self._frames(evaluate(self.source))["north-low"]
        self.assertEqual(north_low["nearest_trunk_segment"], "mid->upper")
        self.assertEqual(north_low["exact_root_flex_zone_id"], "north-low-branch-flex")
        self.assertEqual(north_low["exact_root_flex_zone_status"], "DECLARED_NOT_DEFORMATION_TESTED")
        self.assertAlmostEqual(north_low["transition_u"], 0.14801958337760968, places=12)
        self.assertAlmostEqual(
            north_low["transition_length_along_first_segment_m"],
            0.0645372173379806,
            places=12,
        )
        self.assertAlmostEqual(north_low["exit_branch_radius_m"], 0.0518915887490702, places=12)
        self.assertAlmostEqual(north_low["exit_centerline_distance_m"], 0.04875371484283564, places=12)
        self.assertAlmostEqual(north_low["exit_local_trunk_radius_m"], 0.10064530359190585, places=12)
        self.assertAlmostEqual(
            north_low["branch_vs_local_trunk_departure_angle_deg"],
            44.370330295008024,
            places=10,
        )
        components = north_low["branch_tangent_components_in_exit_frame"]
        self.assertAlmostEqual(components["axial_along_trunk"], 0.7148348933173425, places=12)
        self.assertAlmostEqual(
            components["radial_away_from_trunk_centerline"],
            0.6944724539616899,
            places=12,
        )
        self.assertAlmostEqual(components["azimuthal_around_trunk"], 0.08197003101385525, places=12)
        self.assertLessEqual(north_low["frame_orthogonality_max_abs_dot"], 1e-9)
        self.assertLessEqual(north_low["branch_tangent_reconstruction_error"], 1e-9)

    def test_all_frames_preserve_exact_transition_lengths(self):
        frames = self._frames(evaluate(self.source))
        expected = {
            "south-low": 0.060865238939307745,
            "north-low": 0.0645372173379806,
            "east-mid": 0.021620222932618765,
            "west-high": 0.036156960642309076,
            "north-top": 0.021221011737572286,
        }
        for branch_id, length in expected.items():
            self.assertAlmostEqual(
                frames[branch_id]["transition_length_along_first_segment_m"],
                length,
                places=12,
            )
            self.assertLessEqual(abs(frames[branch_id]["boundary_residual_m"]), 1e-12)

    def test_missing_exact_root_flex_declaration_fails_closed(self):
        candidate = copy.deepcopy(self.source)
        candidate["flex_zones"] = [
            zone for zone in candidate["flex_zones"] if zone["id"] != "north-low-branch-flex"
        ]
        with self.assertRaisesRegex(ValueError, "requires exactly one flex declaration"):
            evaluate(candidate)

    def test_promoted_flex_status_fails_closed(self):
        candidate = copy.deepcopy(self.source)
        candidate["flex_zones"][0]["status"] = "DEFORMATION_PROVEN"
        with self.assertRaisesRegex(ValueError, "all source flex declarations must remain unproven"):
            evaluate(candidate)

    def test_truth_boundary_refuses_topology_rigging_biology_and_runtime_promotion(self):
        report = evaluate(self.source)
        handoff = report["handoff"]
        boundary = report["truth_boundary"]
        self.assertEqual(handoff["connected_topology_state"], "HELD_FOR_GEOMETRY")
        self.assertFalse(handoff["frame_is_weld_ring"])
        self.assertFalse(handoff["frame_is_skinning_or_joint_frame"])
        self.assertFalse(handoff["source_compensation_authorized"])
        self.assertTrue(boundary["authored_centerlines_and_radii_measured"])
        self.assertTrue(boundary["existing_transition_owner_reused"])
        self.assertFalse(boundary["source_geometry_changed"])
        self.assertFalse(boundary["generated_mesh_connectivity_inspected"])
        self.assertFalse(boundary["connected_branch_trunk_topology_proven"])
        self.assertFalse(boundary["junction_strategy_selected"])
        self.assertFalse(boundary["deformation_simulated"])
        self.assertFalse(boundary["rigging_hierarchy_or_weights_inferred"])
        self.assertFalse(boundary["biological_attachment_or_rom_claimed"])
        self.assertFalse(boundary["runtime_readiness_claimed"])

    def test_report_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))


if __name__ == "__main__":
    unittest.main()
