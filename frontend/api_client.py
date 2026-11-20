import json
import os
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ApiError(Exception):
    """A network or API error that is safe to show in the desktop UI."""


class ApiClient:
    def __init__(self, base_url=None, timeout=5):
        configured_url = base_url or os.environ.get(
            "EXAM_API_URL", "http://127.0.0.1:8000"
        )
        self.base_url = configured_url.rstrip("/")
        self.timeout = timeout
        self.token = None

    def request(self, method, path, payload=None):
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method.upper(),
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                if response.status == 204:
                    return None
                content = response.read()
        except HTTPError as error:
            try:
                details = json.loads(error.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                details = {}
            message = details.get("error", f"Backend returned HTTP {error.code}.")
            raise ApiError(message) from error
        except (URLError, TimeoutError, OSError) as error:
            raise ApiError(
                "Could not connect to the backend. Start it with "
                "`python manage.py runserver 127.0.0.1:8000` from `backend/`."
            ) from error

        if not content:
            return None
        try:
            return json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ApiError("The backend returned an invalid response.") from error

    def status(self):
        return self.request("GET", "/api/status/")

    def login(self, username, password):
        response = self.request(
            "POST",
            "/api/auth/login/",
            {"username": username, "password": password},
        )
        self.token = response["token"]
        return response["account"]

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
        filtered = {key: value for key, value in params.items() if value}
        suffix = f"?{urlencode(filtered)}" if filtered else ""
        return f"{path}{suffix}"

    def post(self, path, payload):
        return self.request("POST", path, payload)

    def put(self, path, payload):
        return self.request("PUT", path, payload)

    def delete(self, path):
        return self.request("DELETE", path)
