# Digital Examination Results Management System

## Project Title
Digital Examination Results Management System

## Introduction
This project is a small Python console application created to demonstrate Object-Oriented Programming in an education-related scenario. It allows a user to enter student information, enter subject scores, validate each score, calculate grades, and display a final examination summary.

## Problem Statement
Manual record-keeping of examination results often leads to mistakes, missing paperwork, and delays in calculating grades. This project provides a simple digital method for recording, validating, and reviewing academic results in a beginner-friendly way.

## Proposed Solution
The system uses Python classes to model students and examination results. During one run, it stores multiple results in a list, checks each score for validity, calculates the appropriate grade, and displays a final summary. The list is temporary: records are not saved when the program exits.

## Objectives
- Record student information
- Record multiple subject results
- Validate examination scores
- Calculate letter grades
- Calculate total score
- Calculate average score
- Calculate overall grade
- Display results clearly in the terminal

## Government Institution Context
This project uses the Ministry of Basic and Senior Secondary Education (MBSSE) in Sierra Leone as the institutional context. It is an academic prototype for learning and demonstration only and is not an official national examination system.

## SDG 4 Alignment
This project is primarily related to SDG 4 – Quality Education. It does not claim to implement SDG 4 directly, but it supports an education-sector digital use case within the broader goal of improving education systems and learning quality.

## OOP Concepts Used
- Classes
- Objects
- Attributes
- Constructors
- Instance methods
- Class method
- Static method
- Object interaction

## Classes and Responsibilities
### Student
The Student class stores student information such as student ID, name, and age.

### ExamResult
The ExamResult class connects a student to a subject, validates the score, and calculates the grade.

## Attributes
### Student
- student_id
- name
- age

### ExamResult
- student
- subject
- score

## Instance Methods
- Student.display_info()
- ExamResult.calculate_grade()
- ExamResult.display_result()

## Class Method
Student.create_student() creates a new Student object from the given values.

## Static Method
ExamResult.is_valid_score(score) checks whether the score is valid and returns True or False.

## Object Interaction
Each ExamResult object contains a Student object. This shows how objects can interact with each other.

## List Data Structure
The program uses a single list named results to store multiple ExamResult objects.

## Grade System
- 70–100 = A
- 60–69 = B
- 50–59 = C
- 40–49 = D
- 0–39 = F

## How to Run
Open the terminal in the project folder and run:

```bash
python main.py
```
If you are using Windows and Python is installed via the launcher, you can also run:

```bash
py main.py
```

## Tests
Run the score-validation regression tests with:

```bash
py -m unittest discover -v
```

The tests use Python's standard library and do not require third-party packages.

## Current Scope and Limitations
- This is a single-user command-line learning prototype. It has no login, account roles, or authorization system.
- Student and result data is held in memory only and is lost when the program exits. There is no database, migration, or environment configuration.
- The current workflow creates and displays results; it does not provide persistent listing, search, update, or delete operations.
- Do not use real student information or treat this prototype as a production records system.

## Example Output
```text
========================================
DIGITAL EXAMINATION RESULTS MANAGEMENT SYSTEM
========================================
Enter Student Information
Enter Student ID: ST001
Enter Student Name: Mohamed
Enter Age: 20

Enter Subject: Python Programming
Enter Score: 78
Grade: A
Do you want to enter another subject? (yes/no): yes

Enter Subject: Database Systems
Enter Score: 65
Grade: B
Do you want to enter another subject? (yes/no): yes

Enter Subject: Software Engineering
Enter Score: 52
Grade: C
Do you want to enter another subject? (yes/no): no

========================================
FINAL RESULT
========================================
Student ID: ST001
Student Name: Mohamed
Age: 20

Subject Results
----------------------------------------
Python Programming          78    A
Database Systems            65    B
Software Engineering        52    C
----------------------------------------
Total Score: 195
Average Score: 65.00
Overall Grade: B
----------------------------------------
Thank you for using the system.
```

## DPG Principles
This project is designed in line with some relevant Digital Public Good (DPG) principles, but it is not officially certified as a DPG.

### Open Source
The project is suitable for a GitHub repository and can be shared publicly.

### Inclusive and Accessible
The program uses a simple terminal interface and does not require expensive software or hardware.

### Privacy Respecting
Only fictional sample data is used. No real student personal information is included.

### Modular and Reusable
The Student and ExamResult classes are separated into different modules and can be adapted for similar educational systems.

## Privacy Considerations
- Use fictional names and student IDs
- Do not use real student records
- Keep the application for academic demonstration only

## Project Structure
```text
Digital-Examination-Results-System/
├── main.py
├── student.py
├── exam_result.py
├── README.md
└── screenshots/
```

## Conclusion
This project demonstrates how simple Python OOP can be used to manage student examination records. It is beginner-friendly, easy to explain, and suitable for a university assignment focused on classes, objects, and object interaction.
# SDGs4-OOP_CONCEPT-BSEM_SEMS3
