import math


class Student:
    """Represents a student in the examination system."""

    def __init__(self, student_id, name, age, programme=None):
        if not self.is_valid_student_id(student_id):
            raise ValueError("Student ID is required.")
        if not self.is_valid_name(name):
            raise ValueError("Name must contain letters and spaces only.")
        if not self.is_valid_age(age):
            raise ValueError("Age must be between 0 and 120.")

        self.student_id = student_id.strip()
        self.name = name.strip()
        self.age = age
        self.programme = programme

    @staticmethod
    def is_valid_student_id(student_id):
        return bool(student_id) and isinstance(student_id, str)

    @staticmethod
    def is_valid_name(name):
        return bool(name) and all(c.isalpha() or c.isspace() for c in name)

    @staticmethod
    def is_valid_age(age):
        return isinstance(age, int) and not isinstance(age, bool) and 0 <= age <= 120

    @classmethod
    def create_student(cls, student_id, name, age, programme=None):
        return cls(student_id, name, age, programme)

    def get_modules(self):
        if self.programme is None:
            return []
        return self.programme.get_modules()

    def display_info(self):
        print(f"Student ID: {self.student_id}")
        print(f"Student Name: {self.name}")
        print(f"Age: {self.age}")
        if self.programme:
            print(f"Programme: {self.programme.code} - {self.programme.name}")
