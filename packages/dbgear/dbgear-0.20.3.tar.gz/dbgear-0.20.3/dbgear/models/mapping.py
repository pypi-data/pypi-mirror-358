import pydantic
import yaml
import pathlib
import os

from .base import BaseSchema
from .schema import Schema
from .schema import SchemaManager
from .datamodel import DataModel
from .exceptions import DBGearEntityExistsError
from .exceptions import DBGearEntityNotFoundError
from .exceptions import DBGearEntityRemovalError


class SharedInfo(BaseSchema):
    environ: str
    mapping: str


class Mapping(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    tenant_name: str | None = pydantic.Field(default=None, exclude=True)
    description: str
    schemas: list[str] = []
    shared: SharedInfo | None = None
    deploy: bool = False

    @classmethod
    def load(cls, folder: str, environ: str, name: str):
        with open(f'{folder}/{environ}/{name}/_mapping.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            name=name,
            **data
        )

    @property
    def instance_name(self) -> str:
        return self.tenant_name or self.name

    def build_schema(self, project_schema: SchemaManager, environ_schema: SchemaManager | None):
        schema = Schema(name=self.name)
        for name in self.schemas:
            if name in project_schema:
                schema.update(project_schema[name])
            if environ_schema is not None and name in environ_schema:
                schema.update(environ_schema[name])
        return schema

    @property
    def datamodels(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/{self.name}/*.yaml')):
            if path.name != '_mapping.yaml':
                schema_name, table_name = path.stem.split('@')
                yield DataModel.load(
                    folder=self.folder,
                    environ=self.environ,
                    map_name=self.name,
                    schema_name=schema_name,
                    table_name=table_name
                )


class MappingManager:

    def __init__(self, folder: str, environ: str):
        self.folder = folder
        self.environ = environ

    def __getitem__(self, key: str) -> Mapping:
        return Mapping.load(self.folder, self.environ, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/*/_mapping.yaml')):
            name = str(path.parent.relative_to(pathlib.Path(self.folder) / self.environ))
            yield Mapping.load(self.folder, self.environ, name)

    def add(self, mapping: Mapping) -> None:
        path = os.path.join(self.folder, mapping.environ, mapping.name)
        if os.path.exists(path):
            raise DBGearEntityExistsError(f'Mapping {mapping.name} already exists in {self.folder}/{mapping.environ}')

        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, '_mapping.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(
                mapping.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def remove(self, name: str) -> None:
        path = os.path.join(self.folder, self.environ, name)
        if not os.path.exists(path):
            raise DBGearEntityNotFoundError(f'Mapping {name} does not exist in {self.folder}/{self.environ}')
        files = [f for f in os.listdir(path) if f != '_mapping.yaml']
        if files:
            raise DBGearEntityRemovalError(f'Cannot remove {path}: files other than _mapping.yaml exist')
        os.remove(os.path.join(path, '_mapping.yaml'))
        os.rmdir(path)
