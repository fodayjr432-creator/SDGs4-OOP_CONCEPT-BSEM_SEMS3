class Module:
    """Represents a module belonging to a programme."""

    def __init__(
        self, code, name, level="1", semester="1", description="",
        record_id=None, programme_id=None,
    ):
        if not code or not name:
            raise ValueError("Module code and name are required.")
        self.code = code.strip().upper()
        self.name = name.strip()
        self.level = level
        self.semester = semester
        self.description = description
        self.active = True
        self.id = record_id
        self.programme_id = programme_id

    def display_info(self):
        print(f"  [{self.code}] {self.name} (Level {self.level}, Sem {self.semester})")


class Programme:
    """Represents an academic programme with associated modules."""

    def __init__(self, code, name, record_id=None):
        if not code or not name:
            raise ValueError("Programme code and name are required.")
        self.code = code.strip().upper()
        self.name = name.strip()
        self.active = True
        self._modules = []
        self.id = record_id
        self.description = ""

    def add_module(self, module):
        if not isinstance(module, Module):
            raise TypeError("Expected a Module instance.")
        if any(m.code == module.code for m in self._modules):
            raise ValueError(f"Module {module.code} already exists in {self.code}.")
        self._modules.append(module)

    def get_modules(self, level=None, semester=None):
        result = [m for m in self._modules if m.active]
        if level is not None:
            result = [m for m in result if m.level == str(level)]
        if semester is not None:
            result = [m for m in result if m.semester == str(semester)]
        return result

    def display_info(self):
        print(f"Programme: {self.code} - {self.name}")
        print("Modules:")
        for m in self._modules:
            m.display_info()
