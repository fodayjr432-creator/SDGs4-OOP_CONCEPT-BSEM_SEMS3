import logging
from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate
from django.db import DatabaseError, connection, transaction
from django.db.models import Avg, Max, Q, Sum
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from apps.academics.models import AcademicYear, Module, Programme, ProgrammeModule
from apps.examinations.models import Examination, Question
from apps.results.models import ExamResult
from apps.students.models import Student
from apps.students.serializers import StudentSerializer

logger = logging.getLogger(__name__)

GRADE_BOUNDARIES = [(Decimal("70"), "A"), (Decimal("60"), "B"), (Decimal("50"), "C"), (Decimal("40"), "D")]


def calculate_grade(score):
    score = Decimal(str(score))
    for boundary, grade in GRADE_BOUNDARIES:
        if score >= boundary:
            return grade
    return "F"


def error_response(message, code=400):
    return Response({"error": message}, status=code)


def serialize_programme(p):
    return {"programme_id": p.programme_id, "programme_code": p.programme_code,
            "programme_name": p.programme_name, "description": p.description,
            "is_active": p.is_active}


def serialize_module(m):
    return {"module_id": m.module_id, "module_code": m.module_code,
            "module_name": m.module_name, "level": m.level, "semester": m.semester,
            "description": m.description, "is_active": m.is_active,
            "programme_ids": list(
                ProgrammeModule.objects.filter(module_id=m.module_id)
                .values_list("programme_id", flat=True)
            )}


def serialize_academic_year(ay):
    return {"academic_year_id": ay.academic_year_id, "year_name": ay.year_name,
            "start_date": ay.start_date, "end_date": ay.end_date,
            "is_current": ay.is_current}


def serialize_student(s):
    return StudentSerializer(s).data


def serialize_exam(e):
    return {"examination_id": e.examination_id, "examination_code": e.examination_code,
            "examination_title": e.examination_title, "module_id": e.module_id,
            "academic_year_id": e.academic_year_id, "examination_type": e.examination_type,
            "examination_date": e.examination_date, "maximum_score": str(e.maximum_score),
            "duration_minutes": e.duration_minutes, "status": e.status}


def serialize_result(r):
    return {"result_id": r.result_id, "student_id": r.student_id,
            "examination_id": r.examination_id, "score": str(r.score),
            "grade": r.grade, "remarks": r.remarks,
            "date_recorded": r.date_recorded, "last_updated": r.last_updated}


@api_view(["GET"])
@permission_classes([AllowAny])
def api_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError as error:
        logger.error("PostgreSQL connection check failed (%s).", type(error).__name__)
        return Response({"status": "unavailable", "database": "postgresql"}, status=503)
    return Response({"status": "ok", "database": "postgresql", "authentication_configured": True,
                     "data_api_available": True})


@api_view(["GET"])
def academic_years(request):
    qs = AcademicYear.objects.all()
    return Response([serialize_academic_year(ay) for ay in qs])


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=401)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
def logout(request):
    if hasattr(request.user, "auth_token"):
        request.user.auth_token.delete()
    return Response({"detail": "Logged out"})


@api_view(["GET"])
def current_user(request):
    u = request.user
    return Response({"id": u.id, "username": u.username, "is_staff": u.is_staff})


# Programmes
@api_view(["GET", "POST"])
def programmes(request):
    if request.method == "GET":
        qs = Programme.objects.all()
        code = request.query_params.get("code")
        if code:
            qs = qs.filter(programme_code__icontains=code)
        return Response([serialize_programme(p) for p in qs])
    data = request.data
    if not data.get("programme_code") or not data.get("programme_name"):
        return error_response("Programme code and name are required.")
    try:
        with transaction.atomic():
            p = Programme.objects.create(
                programme_code=data["programme_code"].strip(),
                programme_name=data["programme_name"].strip(),
                description=data.get("description"),
                is_active=data.get("is_active", True),
            )
    except IntegrityError:
        return error_response("A programme with that code or name already exists.", 409)
    return Response(serialize_programme(p), status=201)


@api_view(["GET", "PUT", "DELETE"])
def programme_detail(request, programme_id):
    try:
        p = Programme.objects.get(pk=programme_id)
    except Programme.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(serialize_programme(p))
    if request.method == "PUT":
        data = request.data
        for f in ["programme_code", "programme_name", "description", "is_active"]:
            if f in data:
                setattr(p, f, data[f])
        p.save()
        return Response(serialize_programme(p))
    p.delete()
    return Response(status=204)


# Modules
@api_view(["GET", "POST"])
def modules(request):
    if request.method == "GET":
        qs = Module.objects.all()
        return Response([serialize_module(m) for m in qs])
    data = request.data
    if not data.get("module_code") or not data.get("module_name"):
        return error_response("Module code and name are required.")
    try:
        with transaction.atomic():
            m = Module.objects.create(
                module_code=data["module_code"].strip(),
                module_name=data["module_name"].strip(),
                level=data.get("level", "1"),
                semester=data.get("semester", "1"),
                description=data.get("description"),
                is_active=data.get("is_active", True),
            )
            prog_id = data.get("programme_id")
            if prog_id:
                ProgrammeModule.objects.create(
                    programme_id=prog_id,
                    module_id=m.module_id,
                )
    except Programme.DoesNotExist:
        return error_response("The selected programme was not found.", 404)
    except IntegrityError:
        return error_response("The module could not be saved.", 409)
    return Response(serialize_module(m), status=201)


@api_view(["GET", "PUT", "DELETE"])
def module_detail(request, module_id):
    try:
        m = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(serialize_module(m))
    if request.method == "PUT":
        data = request.data
        for f in ["module_code", "module_name", "level", "semester", "description", "is_active"]:
            if f in data:
                setattr(m, f, data[f])
        m.save()
        return Response(serialize_module(m))
    m.delete()
    return Response(status=204)


# Students
@api_view(["GET", "POST"])
def students(request):
    if request.method == "GET":
        qs = Student.objects.all()
        prog = request.query_params.get("programme")
        search = request.query_params.get("search", "").strip()
        if prog:
            qs = qs.filter(programme_id=prog)
        if search:
            qs = qs.filter(
                Q(admission_number__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return Response([serialize_student(s) for s in qs])
    serializer = StudentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        with transaction.atomic():
            student = serializer.save()
    except IntegrityError:
        return error_response(
            "The student could not be saved because a database constraint was violated.",
            status.HTTP_409_CONFLICT,
        )
    return Response(serialize_student(student), status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def student_detail(request, student_id):
    try:
        s = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(serialize_student(s))
    if request.method == "PUT":
        serializer = StudentSerializer(s, data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                student = serializer.save()
        except IntegrityError:
            return error_response(
                "The student could not be updated because a database constraint was violated.",
                status.HTTP_409_CONFLICT,
            )
        return Response(serialize_student(student))
    if ExamResult.objects.filter(student_id=s.student_id).exists():
        return error_response(
            "This student has examination results and cannot be deleted.",
            status.HTTP_409_CONFLICT,
        )
    try:
        with transaction.atomic():
            s.delete()
    except (IntegrityError, ProtectedError):
        return error_response(
            "This student is referenced by other records and cannot be deleted.",
            status.HTTP_409_CONFLICT,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


# Examinations
@api_view(["GET", "POST"])
def examinations(request):
    if request.method == "GET":
        qs = Examination.objects.all()
        return Response([serialize_exam(e) for e in qs])
    data = request.data
    required = (
        "examination_code",
        "examination_title",
        "module_id",
        "academic_year_id",
        "examination_type",
    )
    if any(not data.get(field) for field in required):
        return error_response("Examination code, title, module, academic year, and type are required.")
    try:
        with transaction.atomic():
            e = Examination.objects.create(
                examination_code=data["examination_code"].strip(),
                examination_title=data["examination_title"].strip(),
                module_id=data["module_id"],
                academic_year_id=data["academic_year_id"],
                examination_type=data["examination_type"],
                examination_date=data.get("examination_date"),
                maximum_score=data.get("maximum_score", 100),
                duration_minutes=data.get("duration_minutes"),
                status=data.get("status", "Draft"),
            )
    except (Module.DoesNotExist, AcademicYear.DoesNotExist):
        return error_response("The selected module or academic year was not found.", 404)
    except (IntegrityError, ValidationError):
        return error_response("The examination could not be saved.", 400)
    return Response(serialize_exam(e), status=201)


@api_view(["GET", "PUT", "DELETE"])
def examination_detail(request, examination_id):
    try:
        e = Examination.objects.get(pk=examination_id)
    except Examination.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(serialize_exam(e))
    if request.method == "PUT":
        data = request.data
        for f in ["examination_code", "examination_title", "module_id", "academic_year_id",
                  "examination_type", "examination_date", "maximum_score", "duration_minutes", "status"]:
            if f in data:
                setattr(e, f, data[f])
        e.save()
        return Response(serialize_exam(e))
    e.delete()
    return Response(status=204)


@api_view(["GET", "POST"])
def examination_questions(request, examination_id):
    if request.method == "GET":
        qs = Question.objects.filter(examination_id=examination_id)
        return Response([{"question_id": q.question_id, "question_text": q.question_text,
                         "question_type": q.question_type, "marks": str(q.marks),
                         "question_order": q.question_order} for q in qs])
    data = request.data
    q = Question.objects.create(
        examination_id=examination_id, question_text=data["question_text"],
        question_type=data["question_type"], options=data.get("options"),
        correct_answer=data.get("correct_answer"), marks=data["marks"],
        question_order=data["question_order"])
    return Response({"question_id": q.question_id}, status=201)


@api_view(["GET", "PUT", "DELETE"])
def question_detail(request, question_id):
    try:
        q = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response({"question_id": q.question_id, "question_text": q.question_text})
    if request.method == "PUT":
        data = request.data
        for f in ["question_text", "question_type", "options", "correct_answer", "marks", "question_order"]:
            if f in data:
                setattr(q, f, data[f])
        q.save()
        return Response({"question_id": q.question_id})
    q.delete()
    return Response(status=204)


# Results
@api_view(["GET", "POST"])
def results(request):
    if request.method == "GET":
        qs = ExamResult.objects.all()
        sid = request.query_params.get("student")
        eid = request.query_params.get("examination")
        if sid:
            qs = qs.filter(student_id=sid)
        if eid:
            qs = qs.filter(examination_id=eid)
        return Response([serialize_result(r) for r in qs])
    data = request.data
    if not data.get("student_id") or not data.get("examination_id") or data.get("score") is None:
        return error_response("Student, examination, and score are required.")
    try:
        score = Decimal(str(data["score"]))
        exam = Examination.objects.get(pk=data["examination_id"])
        Student.objects.only("student_id").get(pk=data["student_id"])
    except InvalidOperation:
        return error_response("Score must be a valid number.")
    except Examination.DoesNotExist:
        return error_response("The selected examination was not found.", 404)
    except Student.DoesNotExist:
        return error_response("The selected student was not found.", 404)
    if score < 0 or score > exam.maximum_score:
        return Response({"error": "Invalid score"}, status=400)
    if ExamResult.objects.filter(student_id=data["student_id"], examination_id=data["examination_id"]).exists():
        return Response({"error": "Duplicate result"}, status=400)
    r = ExamResult.objects.create(
        student_id=data["student_id"], examination_id=data["examination_id"],
        score=score, grade=calculate_grade(score), remarks=data.get("remarks"))
    return Response(serialize_result(r), status=201)


@api_view(["GET", "PUT", "DELETE"])
def result_detail(request, result_id):
    try:
        r = ExamResult.objects.get(pk=result_id)
    except ExamResult.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(serialize_result(r))
    if request.method == "PUT":
        data = request.data
        if "score" in data:
            try:
                score = Decimal(str(data["score"]))
            except InvalidOperation:
                return Response({"error": "Score must be a valid number."}, status=400)
            if score < 0 or score > r.examination.maximum_score:
                return Response({"error": "Invalid score"}, status=400)
            r.score = score
            r.grade = calculate_grade(score)
        if "remarks" in data:
            r.remarks = data["remarks"]
        r.save()
        return Response(serialize_result(r))
    r.delete()
    return Response(status=204)


# Reports
@api_view(["GET"])
def reports(request):
    report = _report_data()
    report["student_reports"] = _student_report_data()
    return Response(report)


def _student_report_data():
    students = (
        Student.objects.select_related("programme")
        .annotate(
            total_score=Sum("exam_results__score"),
            average_score=Avg("exam_results__score"),
        )
        .order_by("admission_number")
    )
    return [
        {
            "student_id": student.admission_number,
            "name": f"{student.first_name} {student.last_name}".strip(),
            "programme": student.programme.programme_code,
            "total_score": round(float(student.total_score or 0), 2),
            "average_score": round(float(student.average_score or 0), 2),
            "overall_grade": calculate_grade(student.average_score or 0),
        }
        for student in students
    ]


def _report_data():
    total_students = Student.objects.count()
    total_programmes = Programme.objects.count()
    total_modules = Module.objects.count()
    total_exams = Examination.objects.count()
    total_results = ExamResult.objects.count()
    passed = ExamResult.objects.filter(grade__in=["A", "B", "C", "D"]).count()
    failed = ExamResult.objects.filter(grade="F").count()
    grade_dist = {}
    for g in ["A", "B", "C", "D", "F"]:
        grade_dist[g] = ExamResult.objects.filter(grade=g).count()
    return {
        "total_students": total_students,
        "total_programmes": total_programmes,
        "total_modules": total_modules,
        "total_examinations": total_exams,
        "total_results": total_results,
        "passed": passed,
        "failed": failed,
        "grade_distribution": grade_dist,
    }


# Dashboard
@api_view(["GET"])
def dashboard(request):
    report = _report_data()
    return Response(
        {
            "counts": {
                "students": report["total_students"],
                "programmes": report["total_programmes"],
                "modules": report["total_modules"],
                "examinations": report["total_examinations"],
                "results": report["total_results"],
            },
            "recent_results": _recent_dashboard_results(),
        }
    )


def _recent_dashboard_results():
    recent_students = (
        ExamResult.objects.values(
            "student_id",
            "student__first_name",
            "student__last_name",
            "student__programme__programme_code",
        )
        .annotate(
            average_score=Avg("score"),
            latest_result=Max("date_recorded"),
        )
        .order_by("-latest_result", "student_id")[:10]
    )
    return [
        {
            "name": (
                f'{student["student__first_name"]} '
                f'{student["student__last_name"]}'
            ).strip(),
            "programme": student["student__programme__programme_code"],
            "average_score": round(float(student["average_score"]), 2),
            "overall_grade": calculate_grade(student["average_score"]),
        }
        for student in recent_students
    ]
