import logging
from decimal import Decimal
from django.contrib.auth import authenticate
from django.db import DatabaseError, connection, transaction
from django.db.models import Q
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
    p = Programme.objects.create(
        programme_code=data["programme_code"], programme_name=data["programme_name"],
        description=data.get("description"), is_active=data.get("is_active", True))
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
    m = Module.objects.create(
        module_code=data["module_code"], module_name=data["module_name"],
        level=data.get("level", "1"), semester=data.get("semester", "1"),
        description=data.get("description"), is_active=data.get("is_active", True))
    prog_id = data.get("programme_id")
    if prog_id:
        ProgrammeModule.objects.create(programme_id=prog_id, module_id=m.module_id)
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
    e = Examination.objects.create(
        examination_code=data["examination_code"], examination_title=data["examination_title"],
        module_id=data["module_id"], academic_year_id=data["academic_year_id"],
        examination_type=data["examination_type"], examination_date=data.get("examination_date"),
        maximum_score=data.get("maximum_score", 100), duration_minutes=data.get("duration_minutes"),
        status=data.get("status", "Draft"))
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
    score = Decimal(str(data["score"]))
    exam = Examination.objects.get(pk=data["examination_id"])
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
            score = Decimal(str(data["score"]))
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
    return Response({
        "total_students": total_students,
        "total_programmes": total_programmes,
        "total_modules": total_modules,
        "total_examinations": total_exams,
        "total_results": total_results,
        "passed": passed,
        "failed": failed,
        "grade_distribution": grade_dist,
    })


# Dashboard
@api_view(["GET"])
def dashboard(request):
    return reports(request)
