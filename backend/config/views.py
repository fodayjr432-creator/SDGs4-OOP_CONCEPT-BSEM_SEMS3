import logging

from django.db import DatabaseError, connection
from rest_framework.decorators import api_view
from rest_framework.response import Response


logger = logging.getLogger(__name__)


@api_view(["GET"])
def api_status(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError as error:
        logger.error(
            "PostgreSQL connection check failed (%s).",
            type(error).__name__,
        )
        return Response(
            {
                "status": "unavailable",
                "database": "postgresql",
                "authentication_configured": False,
                "data_api_available": False,
            },
            status=503,
        )

    return Response(
        {
            "status": "ok",
            "database": "postgresql",
            "authentication_configured": False,
            "data_api_available": False,
        }
    )


@api_view(["GET", "POST", "PUT", "DELETE"])
def data_api_unavailable(request, *args, **kwargs):
    return Response(
        {
            "error": (
                "Academic data access is disabled until authentication and "
                "authorization are implemented for the existing database."
            )
        },
        status=503,
    )


login = data_api_unavailable
logout = data_api_unavailable
programmes = data_api_unavailable
programme_detail = data_api_unavailable
modules = data_api_unavailable
module_detail = data_api_unavailable
students = data_api_unavailable
student_detail = data_api_unavailable
examinations = data_api_unavailable
examination_detail = data_api_unavailable
examination_questions = data_api_unavailable
question_detail = data_api_unavailable
results = data_api_unavailable
result_detail = data_api_unavailable
reports = data_api_unavailable
dashboard = data_api_unavailable
