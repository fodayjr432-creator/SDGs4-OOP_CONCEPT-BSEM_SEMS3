import os
from urllib.parse import urlencode

import requests


class ApiError(Exception):
    """A network or API error that is safe to show in the desktop UI."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url=None, timeout=5):
        configured_url = base_url or os.environ.get(
            "EXAM_API_URL", "http://127.0.0.1:8000"
        )
        self.base_url = configured_url.rstrip("/")
        self.timeout = timeout
        self.token = None
        self._session = requests.Session()

    def request(self, method, path, payload=None):
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        try:
            response = self._session.request(
                method.upper(),
                f"{self.base_url}{path}",
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
        except requests.RequestException as error:
            raise ApiError(
                "Could not connect to the backend. Start it with "
                "`python manage.py runserver 127.0.0.1:8000` from `backend/`."
            ) from error

        if response.status_code == 401:
            self.token = None
        if response.status_code >= 400:
            try:
                details = response.json()
            except requests.exceptions.JSONDecodeError:
                details = {}
            message = details.get("error") if isinstance(details, dict) else None
            if not message and isinstance(details, dict):
                message = details.get("detail")
            if not message and isinstance(details, dict):
                message = next(
                    (
                        str(value[0] if isinstance(value, list) else value)
                        for key, value in details.items()
                        if key != "detail" and value
                    ),
                    None,
                )
            if not message:
                message = f"Backend returned HTTP {response.status_code}."
            raise ApiError(str(message), status_code=response.status_code)

        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as error:
            raise ApiError("The backend returned an invalid response.") from error

    def status(self):
        return self.request("GET", "/api/status/")

    def login(self, username, password):
        response = self.request(
            "POST",
            "/api/auth/login/",
            {"username": username, "password": password},
        )
        token = response.get("token") if isinstance(response, dict) else None
        if not isinstance(token, str) or not token:
            raise ApiError("The backend returned an invalid authentication response.")
        self.token = token
        return response

    def register_institution_administrator(
        self,
        institution_name,
        administrator_name,
        username,
        email,
        password,
        confirm_password,
    ):
        return self.request(
            "POST",
            "/api/auth/register/",
            {
                "institution_name": institution_name,
                "administrator_name": administrator_name,
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm_password,
            },
        )

    def registration_status(self):
        return self.request("GET", "/api/auth/registration-status/")

    def logout(self):
        if self.token:
            try:
                self.request("POST", "/api/auth/logout/")
            finally:
                self.token = None

    def get(self, path):
        return self.request("GET", path)

    @staticmethod
    def query_path(path, **params):
        filtered = {key: value for key, value in params.items() if value not in (None, "")}
        suffix = f"?{urlencode(filtered)}" if filtered else ""
        return f"{path}{suffix}"

    def post(self, path, payload):
        return self.request("POST", path, payload)

    def put(self, path, payload):
        return self.request("PUT", path, payload)

    def delete(self, path):
        return self.request("DELETE", path)

    def list_students(self, search="", programme=None):
        params = {}
        if search:
            params["search"] = search
        if programme is not None:
            params["programme"] = programme
        path = "/api/students/"
        if params:
            path = f"{path}?{urlencode(params)}"
        return self.get(path)

    def get_student(self, student_id):
        return self.get(f"/api/students/{student_id}/")

    def create_student(self, payload):
        return self.post("/api/students/", payload)

    def update_student(self, student_id, payload):
        return self.put(f"/api/students/{student_id}/", payload)

    def delete_student(self, student_id):
        return self.delete(f"/api/students/{student_id}/")

    def close(self):
        self._session.close()
