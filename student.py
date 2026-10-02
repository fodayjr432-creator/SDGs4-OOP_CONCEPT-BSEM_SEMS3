class Student:
    """Represents a student in the examination system."""

    def __init__(self, student_id, name, age):
        self.student_id = student_id
        self.name = name
        self.age = age

    def display_info(self):
        """Display the basic information of a student."""
        print(f"Student ID: {self.student_id}")
        print(f"Student Name: {self.name}")
        print(f"Age: {self.age}")

    @classmethod
    def create_student(cls, student_id, name, age):
        """Create and return a new Student object."""
        return cls(student_id, name, age)
