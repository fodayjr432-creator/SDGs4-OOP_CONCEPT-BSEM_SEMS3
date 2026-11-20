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
