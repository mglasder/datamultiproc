import pickle
from abc import ABCMeta
from pathlib import Path
from typing import List, Tuple, TypeVar, Type
from pydantic import BaseModel

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


class Aggregate(BaseModel, metaclass=ABCMeta):
    class Config:
        allow_mutation = True
        validate_assignment = True
        arbitrary_types_allowed = True

    def write_file(self, path: Path):

        extension = path.suffix
        if extension not in [".pkl", ".pickle"]:
            raise TypeError(f"File extension {extension} is not supported")

        obj = self.dict()

        try:
            with path.open("wb") as f:
                obj_str = pickle.dumps(obj)
                return f.write(obj_str)

        except Exception as ex:
            raise TypeError(f"Could not dump {self} into {path}") from ex

    @classmethod
    def read_file(cls: Type[PydanticModel], path: Path):

        if not path.exists():
            raise FileNotFoundError(str(path))

        extension = path.suffix
        if extension not in [".pkl", ".pickle"]:
            raise TypeError(f"File extension {extension} is not supported")

        try:
            with path.open("rb") as f:
                obj = pickle.loads(f.read())
                return cls.parse_obj(obj)

        except Exception as ex:
            raise TypeError(f"Could load {cls} from {path}") from ex


class BaseSample(Aggregate):
    processing_history: List[Tuple[str, str]] = []
    id: str
