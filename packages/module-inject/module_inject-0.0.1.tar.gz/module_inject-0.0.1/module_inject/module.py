import sys
import types
import typing
import importlib
from pathlib import Path


def get_import_path(filepath: Path) -> str:
    """Find module's import path using sys.path"""
    for library in map(lambda x: Path(x).absolute(), sys.path):
        if filepath.is_relative_to(library):
            path = filepath.relative_to(library)
            break
    else:
        raise ValueError("Module import path not found")

    return ".".join(path.parts[:-1] + (path.stem,))


class Module:
    instances: dict[str, "Module"] = {}

    def __init__(self, importpath: str) -> None:
        self.import_path: str = importpath
        self.namespace: dict[str, typing.Any] = {}

        Module.instances[importpath] = self

    @classmethod
    def from_path(cls, path: Path) -> "Module":
        """Get or create instance using filesystem path"""
        import_path = get_import_path(path.absolute())

        return cls.from_import_path(import_path)

    @classmethod
    def from_import_path(cls, import_path: str) -> "Module":
        """Get or create instance using import path"""
        if import_path in cls.instances:
            return cls.instances[import_path]

        return cls(import_path)

    def set(self, **kwargs: typing.Any) -> None:
        """
        Set values into module's namespace. Shortcut for Module.namespace.update()
        """
        self.namespace.update(kwargs)

    def load(self) -> types.ModuleType:
        """Import the module"""
        return importlib.import_module(self.import_path)
