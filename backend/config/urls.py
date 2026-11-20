from django.urls import path

from . import views

urlpatterns = [
    path("api/status/", views.api_status, name="api-status"),
    path("api/auth/login/", views.login, name="login"),
    path("api/auth/logout/", views.logout, name="logout"),
    path("api/programmes/", views.programmes, name="programmes"),
    path(
        "api/programmes/<int:programme_id>/",
        views.programme_detail,
        name="programme-detail",
    ),
    path("api/modules/", views.modules, name="modules"),
    path(
        "api/modules/<int:module_id>/",
        views.module_detail,
        name="module-detail",
    ),
    path("api/students/", views.students, name="students"),
    path(
        "api/students/<int:student_id>/",
        views.student_detail,
        name="student-detail",
    ),
    path("api/examinations/", views.examinations, name="examinations"),
    path(
        "api/examinations/<int:examination_id>/",
        views.examination_detail,
        name="examination-detail",
    ),
    path(
        "api/examinations/<int:examination_id>/questions/",
        views.examination_questions,
        name="examination-questions",
    ),
    path(
        "api/questions/<int:question_id>/",
        views.question_detail,
        name="question-detail",
    ),
    path("api/results/", views.results, name="results"),
    path(
        "api/results/<int:result_id>/",
        views.result_detail,
        name="result-detail",
    ),
    path("api/reports/", views.reports, name="reports"),
    path("api/dashboard/", views.dashboard, name="dashboard"),
]
