class ExamResult:
    """Represents a student's exam result for one subject."""

    def __init__(self, student, subject, score):
        if student is None:
            raise ValueError("A valid Student object is required.")

        if not self.is_valid_score(score):
            raise ValueError("Score must be between 0 and 100.")

        self.student = student
        self.subject = subject
        self.score = score

    @staticmethod
    def is_valid_score(score):
        """Validate whether the score is between 0 and 100."""
        return isinstance(score, (int, float)) and 0 <= score <= 100

    def calculate_grade(self):
        """Calculate the grade for the score."""
        if self.score >= 70:
            return "A"
        elif self.score >= 60:
            return "B"
        elif self.score >= 50:
            return "C"
        elif self.score >= 40:
            return "D"
        else:
            return "F"

    def display_result(self):
        """Display the result for one subject."""
        print(f"Student: {self.student.name}")
        print(f"Subject: {self.subject}")
        print(f"Score: {self.score}")
        print(f"Grade: {self.calculate_grade()}")
