from django.urls import include, path

from apps.accounts import views as account_views
from . import views

urlpatterns = [
    path("api/status/", views.api_status, name="api-status"),
    path(
        "api/auth/registration-status/",
        account_views.registration_status,
        name="registration-status",
    ),
    path(
        "api/auth/register/",
        account_views.register_initial_administrator,
        name="register-initial-administrator",
    ),
    path("api/auth/login/", account_views.login, name="login"),
    path("api/auth/logout/", account_views.logout, name="logout"),
    path("api/auth/me/", account_views.current_user, name="current-user"),
    path(
        "api/auth/institution/",
        account_views.institution_detail,
        name="institution-detail",
    ),
    path(
        "api/auth/admins/",
        account_views.administrators,
        name="administrators",
    ),
    path(
        "api/auth/admins/<int:user_id>/",
        account_views.administrator_detail,
        name="administrator-detail",
    ),
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
    path("api/academic-years/", views.academic_years, name="academic-years"),
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
    path("api/", include("apps.audit.urls")),
]
