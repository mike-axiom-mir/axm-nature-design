from __future__ import annotations

import unittest

from axm_nature_design import rear_tree_rigging as historical


class HistoricalRearTreeRootSocketRiggingTests(unittest.TestCase):
    def test_historical_receiver_contract_remains_frozen(self):
        self.assertEqual(
            historical.RESULT,
            "PASS_NORTH_TOP_ROOT_SOCKET_RIGID_CHILD_ARTICULATION_DIAGNOSTIC_MINUS5_TO_PLUS5",
        )
        self.assertEqual(
            historical.EXPECTED_MESH_DIGEST,
            "d7fc5deaa1c12d1d8c7d7b6dc95bf1e8544ce26140ee2e4a7d2c67a2c4133e48",
        )
        self.assertEqual(historical.REPRESENTATIVE_ANGLES_DEG, (-5.0, -2.5, 0.0, 2.5, 5.0))
        self.assertEqual(historical.DIAGNOSTIC_MIN_DEG, -5.0)
        self.assertEqual(historical.DIAGNOSTIC_MAX_DEG, 5.0)


if __name__ == "__main__":
    unittest.main()
