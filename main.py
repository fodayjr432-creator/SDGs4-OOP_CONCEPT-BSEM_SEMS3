import math

from student import Student
from exam_result import ExamResult
from programme import Programme
from examination import Examination, Question
from storage import RecordStore


def build_programme_catalogue():
    """Build the default programme catalogue with modules."""
    ce = Programme("CE", "BSc Computer Engineering")
    for code, name, lvl, sem in [
        ("PF", "Programming Fundamentals", "1", "1"),
        ("CE", "Computer Engineering Principles", "1", "1"),
        ("DSA", "Data Structures and Algorithms", "2", "1"),
        ("DBMS", "Database Management Systems", "2", "2"),
        ("CN", "Computer Networks", "3", "1"),
        ("ES", "Embedded Systems", "3", "1"),
        ("VLSI", "VLSI Design", "3", "2"),
    ]:
        from programme import Module
        ce.add_module(Module(code, name, lvl, sem))

    bict = Programme("BICT", "BSc Information and Communication Technology")
    for code, name, lvl, sem in [
        ("PF", "Programming Fundamentals", "1", "1"),
        ("CS", "Computer Systems", "1", "1"),
        ("DBMS", "Database Management Systems", "2", "1"),
        ("WD", "Web Development", "2", "2"),
        ("CN", "Computer Networks", "3", "1"),
        ("SAD", "Systems Analysis and Design", "2", "2"),
        ("IS", "Information Security", "3", "2"),
    ]:
        from programme import Module
        bict.add_module(Module(code, name, lvl, sem))

    bse = Programme("BSE", "BSc Software Engineering")
    for code, name, lvl, sem in [
        ("PF", "Programming Fundamentals", "1", "1"),
        ("OOP", "Object-Oriented Programming", "1", "2"),
        ("DSA", "Data Structures and Algorithms", "2", "1"),
        ("DBMS", "Database Management Systems", "2", "2"),
        ("SEP", "Software Engineering Principles", "3", "1"),
        ("WAD", "Web Application Development", "3", "2"),
        ("ST", "Software Testing", "3", "2"),
    ]:
        from programme import Module
        bse.add_module(Module(code, name, lvl, sem))

    return [ce, bict, bse]


def get_valid_name():
    while True:
        name = input("Enter Student Name: ").strip()
        if name and all(c.isalpha() or c.isspace() for c in name):
            return name
        print("Invalid name. Please enter a name using letters and spaces only.")


def get_valid_age():
    while True:
        age_input = input("Enter Age: ").strip()
        try:
            age = int(age_input)
            if age < 0 or age > 120:
                raise ValueError
            return age
        except ValueError:
            print("Invalid age. Please enter your age as a whole number (0-120).")


def get_valid_score():
    while True:
        score_input = input("Enter Score: ").strip()
        try:
            score = float(score_input)
        except ValueError:
            print("Invalid score. Please enter a numeric score between 0 and 100.")
            continue
        if not math.isfinite(score) or score < 0 or score > 100:
            print("Invalid score. Please enter a numeric score between 0 and 100.")
            continue
        return score


def calculate_overall_grade(average_score):
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
    print("=" * 40)
    print("DIGITAL EXAMINATION RESULTS MANAGEMENT SYSTEM")
    print("=" * 40)
    print()
    print("1. Enter examination results")
    print("2. Delete a student record")
    choice = input("Select option: ").strip()

    if choice == "2":
        store = RecordStore()
        ids = store.list_ids()
        if not ids:
            print("No records found.")
            return
        print("Existing student IDs:", ", ".join(ids))
        sid = input("Enter Student ID to delete: ").strip()
        if store.delete_by_id(sid):
            print(f"Record for {sid} deleted.")
        else:
            print(f"No record found for {sid}.")
        return

    print()

    programmes = build_programme_catalogue()
    print("Available Programmes:")
    for i, p in enumerate(programmes, 1):
        print(f"  {i}. {p.code} - {p.name}")
    while True:
        choice = input("Select programme (number): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(programmes):
                programme = programmes[idx]
                break
        except ValueError:
            pass
        print("Invalid selection. Try again.")

    student_id = input("Enter Student ID: ").strip()
    student_name = get_valid_name()
    age = get_valid_age()

    try:
        student = Student.create_student(student_id, student_name, age, programme)
    except ValueError as e:
        print(f"Registration error: {e}")
        return

    print(f"\nRegistered: {student.name} ({student.student_id})")
    print(f"Programme: {programme.code} - {programme.name}")
    print("\nModules for your programme:")
    for m in student.get_modules():
        m.display_info()

    results = []
    while True:
        subject = input("\nEnter Subject/Module: ").strip()
        if not subject:
            print("Subject cannot be empty.")
            continue
        score = get_valid_score()
        try:
            result = ExamResult(student, subject, score)
            results.append(result)
            print(f"Calculated Grade: {result.calculate_grade()}")
        except ValueError as e:
            print(f"Error: {e}")

        another = input("Do you want to enter another subject/module? (yes/no): ").strip().lower()
        if another != "yes":
            break

    if not results:
        print("No results entered.")
        return

    total_score = sum(r.score for r in results)
    number_of_subjects = len(results)
    average_score = total_score / number_of_subjects
    overall_grade = calculate_overall_grade(average_score)

    print("\n" + "=" * 40)
    print("FINAL EXAMINATION RESULTS")
    print("=" * 40)
    print(f"Student ID: {student.student_id}")
    print(f"Student Name: {student.name}")
    print(f"Age: {student.age}")
    print(f"Programme: {programme.code} - {programme.name}")

    print("\n" + "-" * 40)
    print("SUBJECT RESULTS")
    print("-" * 40)
    for result in results:
        print(f"Subject: {result.subject}")
        print(f"Score: {result.score}")
        print(f"Grade: {result.calculate_grade()}")
        print()

    store = RecordStore()
    record = {
        "student_id": student.student_id,
        "name": student.name,
        "age": student.age,
        "programme": programme.code,
        "results": [{"subject": r.subject, "score": r.score, "grade": r.calculate_grade()} for r in results],
        "total_score": total_score,
        "average_score": round(average_score, 2),
        "overall_grade": overall_grade,
    }
    store.append(record)
    print("Record saved to records.json")
    print(f"Number of Subjects: {number_of_subjects}")
    print(f"Average Score: {average_score:.2f}")
    print(f"Overall Grade: {overall_grade}")
    print("-" * 40)
    print("\nThank you for using the system.")


if __name__ == "__main__":
    main()
