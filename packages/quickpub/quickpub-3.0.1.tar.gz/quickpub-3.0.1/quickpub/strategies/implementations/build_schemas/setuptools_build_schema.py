import os
import sys
from pathlib import Path
from typing import Literal

from danielutils import info, file_exists, LayeredCommand, delete_file

from ...build_schema import BuildSchema


class SetuptoolsBuildSchema(BuildSchema):
    def __init__(self, setup_file_path: str = "./setup.py", backend: Literal["toml"] = "toml") -> None:
        self._backend = backend
        self._setup_file_path = setup_file_path

    def build(self, verbose: bool = False, *args, **kwargs) -> None:
        if not file_exists(self._setup_file_path):
            raise self.EXCEPTION_TYPE(f"Could not find {self._setup_file_path} file")
        if verbose:
            info("Creating new distribution...")
        sources_file_path: str = str(os.path.join(
            str(Path(self._setup_file_path).parent.resolve()), "quickpub.egg-info/SOURCES.txt"))
        delete_file(sources_file_path)
        with LayeredCommand() as exc:
            ret, stdout, stderr = exc(sys.executable + " " + self._setup_file_path + " sdist")
        if ret != 0:
            raise self.EXCEPTION_TYPE(stderr)


__all__ = [
    "SetuptoolsBuildSchema",
]
