from api_client import ApiClient, ApiError
from examination import Examination, Question
from programme import Module, Programme


class AppState:
    def __init__(self, username="Administrator", api_client=None, account=None):
        self.username = username
        self.account = account or {"username": username, "role": "admin"}
        self.api = api_client or ApiClient()
        self.programmes = []
        self.modules = []
        self.examinations = []
        self.refresh_reference_data()

    @property
    def is_admin(self):
        return self.account.get("role") == "admin"

    def refresh_reference_data(self):
        programme_rows = self.api.get("/api/programmes/")
        module_rows = self.api.get("/api/modules/")
        examination_rows = self.api.get("/api/examinations/")

        programmes_by_id = {}
        self.programmes = []
        for item in programme_rows:
            programme = Programme(item["code"], item["name"], item["id"])
            programme.description = item["description"]
            programme.active = bool(item["active"])
            programmes_by_id[programme.id] = programme
            self.programmes.append(programme)

        self.modules = []
        for item in module_rows:
            module = Module(
                item["code"],
                item["name"],
                item["level"],
                item["semester"],
                item["description"],
                item["id"],
                item["programme_id"],
            )
            module.active = bool(item["active"])
            programme = programmes_by_id.get(module.programme_id)
            if programme is not None:
                programme.add_module(module)
            self.modules.append(module)

        self.examinations = []
        for item in examination_rows:
            examination = Examination(
                item["exam_id"],
                item["title"],
                item["module_code"],
                item["total_marks"],
                item["duration_minutes"],
                item["id"],
                item["module_id"],
            )
            examination.status = item["status"]
            examination.exam_type = item["exam_type"]
            examination.exam_date = item["exam_date"]
            for question_data in item.get("questions", []):
                examination.add_question(
                    Question(
                        question_data["question_id"],
                        question_data["text"],
                        question_data["question_type"],
                        question_data["options"],
                        question_data.get("correct_answer"),
                        question_data["marks"],
                        question_data["id"],
                    )
                )
            self.examinations.append(examination)

    def load_records(self):
        students = self.api.get("/api/students/")
        results = self.api.get("/api/results/")
        by_record_id = {student["id"]: student for student in students}
        for student in students:
            student["results"] = []
        for result in results:
            student = by_record_id.get(result["student_record_id"])
            if student is not None:
                student["results"].append(
                    {
                        "id": result["id"],
                        "exam_id": result["exam_id"],
                        "examination_record_id": result["examination_record_id"],
                        "subject": result["subject"],
                        "score": result["score"],
                        "grade": result["grade"],
                        "remarks": result["remarks"],
                    }
                )
        for student in students:
            student["average_score"] = round(student["average_score"], 2)
        return students

    def load_results(self, query=""):
        return self.api.get(self.api.query_path("/api/results/", q=query))

    def load_reports(self, query="", programme=""):
        return self.api.get(
            self.api.query_path("/api/reports/", q=query, programme=programme)
        )

    def load_dashboard(self):
        return self.api.get("/api/dashboard/")

    def _programme_id(self, code):
        programme = next(
            (item for item in self.programmes if item.code == code), None
        )
        if programme is None:
            raise ValueError("Select an existing programme.")
        return programme.id

    def save_record(self, record):
        payload = {
            "student_id": record["student_id"],
            "name": record["name"],
            "age": record["age"],
            "programme_id": self._programme_id(record["programme"]),
        }
        created = self.api.post("/api/students/", payload)
        return created

    def update_student(self, student_record_id, record):
        payload = {
            "student_id": record["student_id"],
            "name": record["name"],
            "age": record["age"],
            "programme_id": self._programme_id(record["programme"]),
        }
        updated = self.api.put(
            f"/api/students/{student_record_id}/", payload
        )
        return updated

    def delete_record(self, student_record_id):
        self.api.delete(f"/api/students/{student_record_id}/")
        return True

    def save_programmes(self):
        try:
            for programme in self.programmes:
                payload = {
                    "code": programme.code,
                    "name": programme.name,
                    "description": programme.description,
                    "active": programme.active,
                }
                if programme.id is None:
                    saved = self.api.post("/api/programmes/", payload)
                    programme.id = saved["id"]
                else:
                    self.api.put(f"/api/programmes/{programme.id}/", payload)
                for module in programme._modules:
                    module_payload = {
                        "programme_id": programme.id,
                        "code": module.code,
                        "name": module.name,
                        "level": str(module.level),
                        "semester": str(module.semester),
                        "description": module.description,
                        "active": module.active,
                    }
                    if module.id is None:
                        saved_module = self.api.post(
                            "/api/modules/", module_payload
                        )
                        module.id = saved_module["id"]
                        module.programme_id = programme.id
                    else:
                        self.api.put(
                            f"/api/modules/{module.id}/", module_payload
                        )
                        module.programme_id = programme.id
            self.refresh_reference_data()
        except ApiError:
            self.refresh_reference_data()
            raise

    def save_examinations(self):
        try:
            for examination in self.examinations:
                payload = {
                    "exam_id": examination.exam_id,
                    "title": examination.title,
                    "module_id": examination.module_id,
                    "exam_type": getattr(examination, "exam_type", "Final"),
                    "total_marks": examination.total_marks,
                    "duration_minutes": examination.duration_minutes,
                    "exam_date": getattr(examination, "exam_date", ""),
                    "status": examination.status,
                }
                if examination.id is None:
                    saved = self.api.post("/api/examinations/", payload)
                    examination.id = saved["id"]
                else:
                    self.api.put(
                        f"/api/examinations/{examination.id}/", payload
                    )
                for question in examination.questions:
                    if question.id is not None:
                        continue
                    saved_question = self.api.post(
                        f"/api/examinations/{examination.id}/questions/",
                        {
                            "question_id": question.question_id,
                            "text": question.text,
                            "question_type": question.question_type,
                            "options": question.options,
                            "correct_answer": question.correct_answer,
                            "marks": question.marks,
                        },
                    )
                    question.id = saved_question["id"]
            self.refresh_reference_data()
        except ApiError:
            self.refresh_reference_data()
            raise

    def add_examination(self, examination):
        if not isinstance(examination, Examination):
            raise TypeError("Expected an Examination instance.")
        self.examinations.append(examination)
        self.save_examinations()

    def add_programme(self, programme):
        if not isinstance(programme, Programme):
            raise TypeError("Expected a Programme instance.")
        self.programmes.append(programme)
        self.save_programmes()

    def save_programme_changes(self):
        self.save_programmes()

    def save_examination_changes(self):
        self.save_examinations()

    def create_result(self, values):
        return self.api.post("/api/results/", values)

    def update_result(self, result_id, values):
        return self.api.put(f"/api/results/{result_id}/", values)

    def delete_result(self, result_id):
        self.api.delete(f"/api/results/{result_id}/")
