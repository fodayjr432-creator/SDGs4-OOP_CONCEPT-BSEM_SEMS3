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
            programme = Programme(
                item["programme_code"],
                item["programme_name"],
                item["programme_id"],
            )
            programme.description = item["description"]
            programme.active = bool(item["is_active"])
            programmes_by_id[programme.id] = programme
            self.programmes.append(programme)

        self.modules = []
        for item in module_rows:
            module = Module(
                item["module_code"],
                item["module_name"],
                item["level"],
                item["semester"],
                item.get("description") or "",
                item["module_id"],
                None,
            )
            module.active = bool(item["is_active"])
            programme_ids = item.get("programme_ids", [])
            module.programme_id = programme_ids[0] if programme_ids else None
            for programme_id in programme_ids:
                programme = programmes_by_id.get(programme_id)
                if programme is not None:
                    programme.add_module(module)
            self.modules.append(module)

        self.examinations = []
        for item in examination_rows:
            module = next(
                (
                    candidate
                    for candidate in self.modules
                    if candidate.id == item["module_id"]
                ),
                None,
            )
            examination = Examination(
                item["examination_code"],
                item["examination_title"],
                module.code if module else "",
                float(item["maximum_score"]),
                item["duration_minutes"] or 60,
                item["examination_id"],
                item["module_id"],
            )
            examination.status = item["status"]
            examination.exam_type = item["examination_type"]
            examination.exam_date = item["examination_date"] or ""
            for question_data in item.get("questions", []):
                examination.add_question(
                    Question(
                        question_data["question_id"],
                        question_data["question_text"],
                        question_data["question_type"],
                        question_data.get("options") or [],
                        question_data.get("correct_answer"),
                        question_data["marks"],
                        question_data["question_id"],
                    )
                )
            self.examinations.append(examination)

    @staticmethod
    def _student_record(item):
        return {
            "id": item["student_id"],
            "student_id": item["admission_number"],
            "name": f'{item["first_name"]} {item["last_name"]}'.strip(),
            "first_name": item["first_name"],
            "last_name": item["last_name"],
            "age": item["age"],
            "programme_id": item["programme_id"],
            "programme": item.get("programme_code", ""),
            "gender": item.get("gender"),
            "is_active": item["is_active"],
            "results": [],
            "total_score": 0,
            "average_score": 0,
            "result_count": 0,
            "overall_grade": "F",
        }

    def _student_records(self, rows):
        programmes = {item.id: item.code for item in self.programmes}
        records = [self._student_record(row) for row in rows]
        for record in records:
            record["programme"] = programmes.get(
                record["programme_id"], record["programme"]
            )
        return records

    def load_students(self, search="", programme=None):
        rows = self.api.list_students(search=search, programme=programme)
        return self._student_records(rows)

    def load_student(self, student_record_id):
        row = self.api.get_student(student_record_id)
        return self._student_records([row])[0]

    def load_records(self):
        students = self.load_students()
        results = self.api.get("/api/results/")
        by_record_id = {student["id"]: student for student in students}
        examinations = {
            item.id: item for item in self.examinations
        }
        for result in results:
            student = by_record_id.get(result["student_id"])
            if student is not None:
                student["results"].append(
                    {
                        "id": result["result_id"],
                        "exam_id": (
                            examinations[result["examination_id"]].exam_id
                            if result["examination_id"] in examinations
                            else str(result["examination_id"])
                        ),
                        "examination_record_id": result["examination_id"],
                        "subject": (
                            examinations[result["examination_id"]].title
                            if result["examination_id"] in examinations
                            else ""
                        ),
                        "score": result["score"],
                        "grade": result["grade"],
                        "remarks": result["remarks"],
                    }
                )
        for student in students:
            scores = [float(result["score"]) for result in student["results"]]
            student["total_score"] = sum(scores)
            student["result_count"] = len(scores)
            student["average_score"] = (
                round(sum(scores) / len(scores), 2) if scores else 0
            )
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
        first_name = record.get("first_name")
        last_name = record.get("last_name")
        if first_name is None or last_name is None:
            first_name, _, last_name = record["name"].partition(" ")
        payload = {
            "admission_number": record["student_id"],
            "first_name": first_name,
            "last_name": last_name,
            "age": record["age"],
            "programme_id": self._programme_id(record["programme"]),
        }
        created = self.api.create_student(payload)
        return created

    def update_student(self, student_record_id, record):
        first_name = record.get("first_name")
        last_name = record.get("last_name")
        if first_name is None or last_name is None:
            first_name, _, last_name = record["name"].partition(" ")
        payload = {
            "admission_number": record["student_id"],
            "first_name": first_name,
            "last_name": last_name,
            "age": record["age"],
            "programme_id": self._programme_id(record["programme"]),
        }
        updated = self.api.update_student(student_record_id, payload)
        return updated

    def delete_record(self, student_record_id):
        self.api.delete_student(student_record_id)
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
