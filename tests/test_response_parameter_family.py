from __future__ import annotations

import copy
import math
import unittest

from axm_nature_design.response_parameter_family import (
    analyze_exact_state_family,
    assemble_family,
    half_sine_weights,
    reconstruct_from_neutral_peak,
)


def mesh(scale: float, offset: float = 0.0) -> dict:
    return {
        "vertices": [
            [0.0 + offset, 0.0, 0.0],
            [1.0 * scale + offset, 0.0, 0.0],
            [0.0 + offset, 1.0 * scale, 0.0],
        ],
        "triangles": [[0, 1, 2]],
        "regions": ["proof"],
    }


def exact_states(neutral: dict, peak: dict) -> list[dict]:
    return [reconstruct_from_neutral_peak(neutral, peak, value) for value in half_sine_weights()]


class ResponseParameterFamilyTests(unittest.TestCase):
    def test_two_materially_different_cases_are_canonical(self) -> None:
        neutral_a = mesh(1.0)
        peak_a = copy.deepcopy(neutral_a)
        peak_a["vertices"][2][0] += 0.18
        neutral_b = mesh(0.6, 2.0)
        peak_b = copy.deepcopy(neutral_b)
        peak_b["vertices"][1][1] += 0.135

        a = analyze_exact_state_family(
            case_id="a",
            source_study="source-a",
            source_digest="digest-a",
            response_ceiling_m=0.18,
            meshes=exact_states(neutral_a, peak_a),
        )
        b = analyze_exact_state_family(
            case_id="b",
            source_study="source-b",
            source_digest="digest-b",
            response_ceiling_m=0.135,
            meshes=exact_states(neutral_b, peak_b),
        )
        forward = assemble_family([a, b])
        reverse = assemble_family([b, a])
        self.assertEqual(forward["family_digest"], reverse["family_digest"])
        self.assertEqual(forward["distinct_source_count"], 2)
        self.assertEqual(forward["distinct_peak_count"], 2)
        self.assertEqual(forward["distinct_response_ceiling_count"], 2)
        self.assertLessEqual(a["max_reconstruction_residual_m"], 1e-12)
        self.assertLessEqual(b["max_reconstruction_residual_m"], 1e-12)

    def test_wrong_phase_count_fails_closed(self) -> None:
        neutral = mesh(1.0)
        peak = copy.deepcopy(neutral)
        peak["vertices"][1][1] += 0.18
        with self.assertRaises(ValueError):
            analyze_exact_state_family(
                case_id="a",
                source_study="source-a",
                source_digest="digest-a",
                response_ceiling_m=0.18,
                meshes=exact_states(neutral, peak)[:-1],
            )

    def test_non_half_sine_state_fails_closed(self) -> None:
        neutral = mesh(1.0)
        peak = copy.deepcopy(neutral)
        peak["vertices"][2][0] += 0.18
        states = exact_states(neutral, peak)
        states[4] = copy.deepcopy(states[4])
        states[4]["vertices"][2][0] += 1e-4
        with self.assertRaises(ValueError):
            analyze_exact_state_family(
                case_id="a",
                source_study="source-a",
                source_digest="digest-a",
                response_ceiling_m=0.18,
                meshes=states,
                tolerance_m=1e-12,
            )

    def test_duplicate_source_identity_fails_closed(self) -> None:
        neutral = mesh(1.0)
        peak = copy.deepcopy(neutral)
        peak["vertices"][1][1] += 0.18
        a = analyze_exact_state_family(
            case_id="a",
            source_study="source-a",
            source_digest="digest-a",
            response_ceiling_m=0.18,
            meshes=exact_states(neutral, peak),
        )
        duplicate = copy.deepcopy(a)
        duplicate["case_id"] = "b"
        duplicate["response_ceiling_m"] = 0.135
        with self.assertRaises(ValueError):
            assemble_family([a, duplicate])

    def test_endpoint_return_is_exact(self) -> None:
        weights = half_sine_weights()
        self.assertEqual(len(weights), 17)
        self.assertEqual(weights[0], 0.0)
        self.assertEqual(weights[-1], 0.0)
        self.assertAlmostEqual(weights[8], 1.0)
        self.assertTrue(all(math.isclose(weights[i], weights[16 - i], abs_tol=1e-15) for i in range(17)))


if __name__ == "__main__":
    unittest.main()
