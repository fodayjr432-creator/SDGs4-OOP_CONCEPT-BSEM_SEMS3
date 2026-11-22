from datetime import datetime, timezone

from django.test import SimpleTestCase

from apps.core.fields import UTCNaiveDateTimeField
from config.views import calculate_grade, normalize_question_type


class AcademicHelperTests(SimpleTestCase):
    def test_grade_uses_percentage_of_examination_maximum(self):
        self.assertEqual(calculate_grade("140.00", "200.00"), "A")
        self.assertEqual(calculate_grade("120.00", "200.00"), "B")
        self.assertEqual(calculate_grade("100.00", "200.00"), "C")
        self.assertEqual(calculate_grade("80.00", "200.00"), "D")
        self.assertEqual(calculate_grade("79.99", "200.00"), "F")

    def test_grade_handles_non_finite_scores_and_invalid_maximum(self):
        self.assertEqual(calculate_grade("NaN"), "F")
        self.assertEqual(calculate_grade("50", "0"), "F")

    def test_question_types_normalize_to_database_values(self):
        self.assertEqual(normalize_question_type("mcq"), "MCQ")
        self.assertEqual(normalize_question_type("true_false"), "TRUE_FALSE")
        self.assertEqual(
            normalize_question_type("SHORT_ANSWER"),
            "SHORT_ANSWER",
        )
        self.assertIsNone(normalize_question_type("essay"))

    def test_naive_database_timestamps_are_interpreted_as_utc(self):
        field = UTCNaiveDateTimeField()
        timestamp = datetime(2026, 11, 22, 12, 0)

        self.assertEqual(
            field.from_db_value(timestamp, None, None),
            timestamp.replace(tzinfo=timezone.utc),
        )
