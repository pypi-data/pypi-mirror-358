# from importlib import import_module
import pydantic
import yaml

from .base import BaseSchema
from .schema import SchemaManager
from .environ import EnvironManager
from .option import Options


class Project(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    project_name: str
    description: str
    options: Options = pydantic.Field(default_factory=Options)

    _schemas: SchemaManager | None = None

    @classmethod
    def load(cls, folder: str):
        with open(f'{folder}/project.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        mgr = cls(
            folder=folder,
            **data
        )
        return mgr

    def save(self) -> None:
        with open(f'{self.folder}/project.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )

    @property
    def schemas(self) -> SchemaManager:
        if self._schemas is None:
            self._schemas = SchemaManager.load(f'{self.folder}/schema.yaml')
        return self._schemas

    @property
    def envs(self) -> EnvironManager:
        return EnvironManager(self.folder)
