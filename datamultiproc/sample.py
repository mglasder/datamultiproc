from abc import ABCMeta
from pathlib import Path
from typing import List, Tuple
from pydantic import BaseModel
from pydantic_yaml import YamlModelMixin


class Aggregate(BaseModel, metaclass=ABCMeta):
    class Config:
        allow_mutation = True
        validate_assignment = True
        arbitrary_types_allowed = True


class BaseSample(YamlModelMixin, Aggregate):
    processing_history: List[Tuple[str, str]] = []
    id: str

    def write_file(self, filepath: Path):
        yml = self.yaml()
        with open(str(filepath), "w") as f:
            f.write(yml)

    def read_file(self, filepath: Path):
        with open(str(filepath), "r") as f:
            yml = f.read()
        self.parse_raw(yml)
