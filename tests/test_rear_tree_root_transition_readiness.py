import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from axm_nature_design.organic_form import load_source
from axm_nature_design.rear_tree_root_transition_readiness import evaluate

SOURCE = ROOT / "examples" / "east_rear_tree_neutral_001.json"


class RearTreeRootTransitionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.source = load_source(SOURCE)

    def _branches(self, report):
        return {row["branch_id"]: row for row in report["branches"]}

    def test_current_source_has_five_measured_neutral_transition_envelopes(self):
        report = evaluate(self.source)
        self.assertEqual(
            report["state"],
            "PASS_EXACT_NEUTRAL_BRANCH_TRANSITION_ENVELOPES__CONNECTED_TOPOLOGY_HELD",
        )
        self.assertEqual(report["branch_count"], 5)
        self.assertTrue(all(report["checks"].values()))
        self.assertAlmostEqual(
            report["minimum_embedded_length_along_first_segment_m"],
            0.021221011737572286,
            places=12,
        )
        self.assertAlmostEqual(
            report["maximum_embedded_length_along_first_segment_m"],
            0.0645372173379806,
            places=12,
        )
        for row in report["branches"]:
            self.assertEqual(
                row["transition_state"],
                "FULL_BRANCH_RADIUS_EXITS_TRUNK_RADIAL_ENVELOPE_WITHIN_FIRST_SEGMENT",
            )
            self.assertGreater(row["root_full_radius_support_margin_m"], 0.0)
            self.assertLess(row["first_segment_end_support_margin_m"], 0.0)
            self.assertIsNotNone(row["first_full_radius_exit_boundary"])
            self.assertLessEqual(
                abs(row["first_full_radius_exit_boundary"]["boundary_residual_m"]),
                1e-12,
            )
            self.assertEqual(row["exact_root_flex_zone_status"], "DECLARED_NOT_DEFORMATION_TESTED")

    def test_north_low_transition_is_source_geometry_not_connected_topology(self):
        report = evaluate(self.source)
        north_low = self._branches(report)["north-low"]
        self.assertEqual(north_low["root_nearest_trunk_segment"], "mid->upper")
        self.assertAlmostEqual(north_low["root_nearest_trunk_segment_t"], 0.5877803557617942, places=12)
        self.assertAlmostEqual(north_low["root_centerline_distance_m"], 0.006592784731672558, places=12)
        self.assertAlmostEqual(north_low["root_local_trunk_radius_m"], 0.10236658932714617, places=12)
        self.assertAlmostEqual(north_low["root_full_radius_support_margin_m"], 0.040773804595473605, places=12)
        self.assertAlmostEqual(north_low["first_segment_length_m"], 0.4360045871318327, places=12)
        self.assertAlmostEqual(north_low["embedded_fraction_of_first_segment"], 0.14801958337760968, places=12)
        self.assertAlmostEqual(north_low["embedded_length_along_first_segment_m"], 0.0645372173379806, places=12)
        boundary = north_low["first_full_radius_exit_boundary"]
        self.assertEqual(boundary["nearest_trunk_segment"], "mid->upper")
        self.assertAlmostEqual(boundary["branch_radius_m"], 0.0518915887490702, places=12)
        self.assertAlmostEqual(boundary["centerline_distance_m"], 0.04875371484283564, places=12)
        self.assertAlmostEqual(boundary["local_trunk_radius_m"], 0.10064530359190585, places=12)
        self.assertEqual(report["handoff"]["connected_topology_state"], "HELD_FOR_GEOMETRY")
        self.assertFalse(report["handoff"]["junction_strategy_selected"])
        self.assertFalse(report["handoff"]["source_compensation_authorized"])

    def test_exact_transition_lengths_remain_branch_specific(self):
        rows = self._branches(evaluate(self.source))
        expected = {
            "south-low": 0.060865238939307745,
            "north-low": 0.0645372173379806,
            "east-mid": 0.021620222932618765,
            "west-high": 0.036156960642309076,
            "north-top": 0.021221011737572286,
        }
        for branch_id, length in expected.items():
            self.assertAlmostEqual(rows[branch_id]["embedded_length_along_first_segment_m"], length, places=12)

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

    def test_zero_length_first_segment_fails_closed(self):
        candidate = copy.deepcopy(self.source)
        branch = next(row for row in candidate["branches"] if row["id"] == "north-low")
        branch["points"][1] = list(branch["points"][0])
        with self.assertRaisesRegex(ValueError, "first segment must have nonzero length"):
            evaluate(candidate)

    def test_truth_boundary_refuses_connectivity_rigging_biology_and_runtime_promotion(self):
        boundary = evaluate(self.source)["truth_boundary"]
        self.assertTrue(boundary["authored_centerlines_and_radii_measured"])
        self.assertFalse(boundary["source_geometry_changed"])
        self.assertFalse(boundary["flex_zone_metadata_changed"])
        self.assertFalse(boundary["generated_mesh_connectivity_inspected"])
        self.assertFalse(boundary["connected_branch_trunk_topology_proven"])
        self.assertFalse(boundary["weld_boolean_or_remesh_strategy_selected"])
        self.assertFalse(boundary["deformation_simulated"])
        self.assertFalse(boundary["rigging_hierarchy_or_weights_inferred"])
        self.assertFalse(boundary["biological_attachment_claimed"])
        self.assertFalse(boundary["runtime_readiness_claimed"])

    def test_report_is_deterministic(self):
        self.assertEqual(evaluate(self.source), evaluate(copy.deepcopy(self.source)))


if __name__ == "__main__":
    unittest.main()
