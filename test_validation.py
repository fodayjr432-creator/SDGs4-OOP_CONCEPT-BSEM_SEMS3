import math
import unittest
from unittest.mock import patch

import main
from exam_result import ExamResult


class ScoreValidationTests(unittest.TestCase):
    def test_model_rejects_non_finite_and_boolean_scores(self):
        for score in (math.nan, math.inf, -math.inf, True):
            with self.subTest(score=score):
                self.assertFalse(ExamResult.is_valid_score(score))

    def test_model_accepts_scores_at_boundaries(self):
        self.assertTrue(ExamResult.is_valid_score(0))
        self.assertTrue(ExamResult.is_valid_score(100))

    def test_cli_reprompts_after_non_finite_score(self):
        with patch("builtins.input", side_effect=["nan", "72"]):
            with patch("builtins.print") as print_mock:
                self.assertEqual(main.get_valid_score(), 72.0)

        print_mock.assert_called_once_with(
            "Invalid score. Please enter a numeric score between 0 and 100."
        )


if __name__ == "__main__":
    unittest.main()