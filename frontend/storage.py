import json
import os


class RecordStore:
    """Simple JSON file-based record storage."""

    def __init__(self, filepath="records.json"):
        self.filepath = filepath

    def save(self, data):
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r") as f:
            return json.load(f)

    def append(self, record):
        records = self.load()
        records.append(record)
        self.save(records)

    def find_by_id(self, student_id):
        for r in self.load():
            if r.get("student_id") == student_id:
                return r
        return None

    def delete_by_id(self, student_id):
        records = self.load()
        filtered = [r for r in records if r.get("student_id") != student_id]
        if len(filtered) == len(records):
            return False
        self.save(filtered)
        return True

    def list_ids(self):
        return [r.get("student_id") for r in self.load()]


class InstitutionNameStore:
    """Persist only the institution name in a separate JSON settings file."""

    def __init__(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "institution_settings.json",
            )
        self.filepath = filepath

    def load(self, default_name):
        if not os.path.exists(self.filepath):
            return default_name
        try:
            with open(self.filepath, "r") as file:
                settings = json.load(file)
            if isinstance(settings, dict):
                name = settings.get("institution_name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
        except (json.JSONDecodeError, OSError):
            pass
        return default_name

    def save(self, institution_name):
        directory = os.path.dirname(self.filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.filepath, "w") as file:
            json.dump({"institution_name": institution_name.strip()}, file, indent=2)
