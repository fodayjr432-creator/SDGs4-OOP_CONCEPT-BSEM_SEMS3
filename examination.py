import math


class Question:
    """Represents a single examination question."""

    def __init__(self, question_id, text, question_type, options=None, correct_answer=None, marks=1):
        if question_type not in ("mcq", "true_false", "short_answer"):
            raise ValueError("Invalid question type.")
        self.question_id = question_id
        self.text = text
        self.question_type = question_type
        self.options = options or []
        self.correct_answer = correct_answer
        self.marks = marks

    def check_answer(self, answer):
        if self.question_type in ("mcq", "true_false"):
            return str(answer).strip().lower() == str(self.correct_answer).strip().lower()
        return None  # short_answer requires manual marking


class Examination:
    """Represents a digital examination."""

    def __init__(self, exam_id, title, module_code, total_marks, duration_minutes=60):
        self.exam_id = exam_id
        self.title = title
        self.module_code = module_code
        self.total_marks = total_marks
        self.duration_minutes = duration_minutes
        self.questions = []
        self.status = "draft"

    def add_question(self, question):
        if not isinstance(question, Question):
            raise TypeError("Expected a Question instance.")
        self.questions.append(question)

    def calculate_score(self, answers):
        """Calculate objective score from a dict of {question_id: answer}."""
        score = 0
        for q in self.questions:
            if q.question_type in ("mcq", "true_false"):
                if q.check_answer(answers.get(q.question_id)):
                    score += q.marks
        return score

    def display_info(self):
        print(f"Exam: {self.exam_id} - {self.title}")
        print(f"Module: {self.module_code}")
        print(f"Total Marks: {self.total_marks}")
        print(f"Duration: {self.duration_minutes} min")
        print(f"Questions: {len(self.questions)}")
        print(f"Status: {self.status}")
