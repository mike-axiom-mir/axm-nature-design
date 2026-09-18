from __future__ import annotations

import json
import unittest
from pathlib import Path

from axm_nature_design.rear_tree_geometry_shared_driver_static_rebind import (
    COMMAND_SIGN_MULTIPLIER_BY_BRANCH,
    RIGGING_SHARED_DRIVER_HEAD,
    SHARED_DRIVER_VALUES_DEG,
    VFX_STATIC_RESPONSE_HEAD,
    _angles_for_shared_driver,
    evaluate,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "examples" / "east_rear_tree_neutral_001.json").read_text())


class SharedDriverStaticGeometryRebindTests(unittest.TestCase):
    def test_exact_five_static_witnesses_preserve_structure(self):
        evidence = evaluate(SOURCE)
        self.assertEqual(evidence["result"], "PASS_SHARED_DRIVER_STATIC_WITNESS_STRUCTURE_REBOUND")
        self.assertEqual(evidence["shared_driver"]["values_deg"], list(SHARED_DRIVER_VALUES_DEG))
        self.assertEqual(evidence["shared_driver"]["state_count"], 5)
        self.assertEqual(evidence["shared_driver"]["prior_geometry_overlap_state_count"], 3)
        self.assertEqual(evidence["shared_driver"]["new_interior_state_count"], 2)
        self.assertEqual(evidence["shared_driver"]["maximum_composition_order_vertex_delta_m"], 0.0)
        self.assertEqual(evidence["shared_driver"]["maximum_globally_fixed_vertex_drift_m"], 0.0)
        self.assertEqual(evidence["shared_driver"]["maximum_pivot_vertex_drift_m"], 0.0)
        self.assertFalse(evidence["truth_boundary"]["continuous_interval_checked"])
        self.assertFalse(evidence["truth_boundary"]["simultaneous_motion_claimed"])

    def test_exact_sign_map(self):
        self.assertEqual(
            COMMAND_SIGN_MULTIPLIER_BY_BRANCH,
            {
                "south-low": 1.0,
                "north-low": -1.0,
                "east-mid": 1.0,
                "west-high": -1.0,
                "north-top": 1.0,
            },
        )
        self.assertEqual(
            _angles_for_shared_driver(2.5),
            {
                "south-low": 2.5,
                "north-low": -2.5,
                "east-mid": 2.5,
                "west-high": -2.5,
                "north-top": 2.5,
            },
        )

    def test_truth_boundaries_fail_closed(self):
        with self.assertRaises(ValueError):
            evaluate(SOURCE, requested_rigging_head="0" * 40)
        with self.assertRaises(ValueError):
            evaluate(SOURCE, requested_vfx_head="0" * 40)
        with self.assertRaises(ValueError):
            evaluate(SOURCE, requested_shared_driver_values=(-5.0, 0.0, 5.0))
        with self.assertRaises(ValueError):
            evaluate(SOURCE, claim_continuous_interval=True)
        with self.assertRaises(ValueError):
            evaluate(SOURCE, claim_simultaneous_motion=True)
        self.assertEqual(len(RIGGING_SHARED_DRIVER_HEAD), 40)
        self.assertEqual(len(VFX_STATIC_RESPONSE_HEAD), 40)


if __name__ == "__main__":
    unittest.main()
