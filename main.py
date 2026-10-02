from student import Student
from exam_result import ExamResult


def get_valid_name():
    """Ask for a valid student name. Only letters and spaces are accepted."""
    while True:
        name = input("Enter Student Name: ").strip()
        if name and all(character.isalpha() or character.isspace() for character in name):
            return name
        print("Invalid name. Please enter a name using letters and spaces only.")


def get_valid_age():
    """Ask for a valid integer age."""
    while True:
        age_input = input("Enter Age: ").strip()
        try:
            age = int(age_input)
            if age < 0:
                raise ValueError
            return age
        except ValueError:
            print("Invalid age. Please enter your age as a whole number.")


def get_valid_subject():
    """Ask for a valid subject or module name."""
    while True:
        subject = input("Enter Subject/Module: ").strip()
        if subject and all(character.isalpha() or character.isspace() or character in "-_/" for character in subject):
            return subject
        print("Invalid subject. Please enter a valid subject name.")


def get_valid_score():
    """Ask for a numeric score between 0 and 100."""
    while True:
        score_input = input("Enter Score: ").strip()
        try:
            score = float(score_input)
        except ValueError:
            print("Invalid score. Please enter a numeric score between 0 and 100.")
            continue

        if score < 0 or score > 100:
            print("Invalid score. Please enter a numeric score between 0 and 100.")
            continue

        return score


def calculate_overall_grade(average_score):
    """Return the overall grade based on the average score."""
    if average_score >= 70:
        return "A"
    elif average_score >= 60:
        return "B"
    elif average_score >= 50:
        return "C"
    elif average_score >= 40:
        return "D"
    else:
        return "F"


def main():
    """Interactive terminal application for managing examination results."""
    print("=" * 40)
    print("DIGITAL EXAMINATION RESULTS MANAGEMENT SYSTEM")
    print("=" * 40)
    print()

    student_id = input("Enter Student ID: ").strip()
    student_name = get_valid_name()
    age = get_valid_age()

    student = Student.create_student(student_id, student_name, age)
    results = []

    while True:
        subject = get_valid_subject()
        score = get_valid_score()

        result = ExamResult(student, subject, score)
        results.append(result)

        print(f"Calculated Grade: {result.calculate_grade()}")

        another_subject = input("Do you want to enter another subject/module? (yes/no): ").strip().lower()
        if another_subject != "yes":
            break

    total_score = sum(result.score for result in results)
    number_of_subjects = len(results)
    average_score = total_score / number_of_subjects if number_of_subjects else 0
    overall_grade = calculate_overall_grade(average_score)

    print("\n" + "=" * 40)
    print("FINAL EXAMINATION RESULTS")
    print("=" * 40)
    print(f"Student ID: {student.student_id}")
    print(f"Student Name: {student.name}")
    print(f"Age: {student.age}")

    print("\n" + "-" * 40)
    print("SUBJECT RESULTS")
    print("-" * 40)

    for result in results:
        print(f"Subject: {result.subject}")
        print(f"Score: {result.score}")
        print(f"Grade: {result.calculate_grade()}")
        print()

    print("-" * 40)
    print(f"Total Score: {total_score}")
    print(f"Number of Subjects: {number_of_subjects}")
    print(f"Average Score: {average_score:.2f}")
    print(f"Overall Grade: {overall_grade}")
    print("-" * 40)
    print("\nThank you for using the system.")


if __name__ == "__main__":
    main()
