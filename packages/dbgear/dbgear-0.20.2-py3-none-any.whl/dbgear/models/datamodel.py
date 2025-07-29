import pydantic
import yaml
import pathlib
import os

from typing import Any

from .base import BaseSchema
from .exceptions import DBGearEntityExistsError
from .exceptions import DBGearEntityRemovalError


class SettingInfo(BaseSchema):
    type: str
    width: int | None = None
    environ: str | None = None
    schema_name: str | None = None
    table_name: str | None = None


class DataSource:
    folder: str
    environ: str
    schema_name: str
    table_name: str
    segment: str | None = None
    data: list[dict[str, Any]]

    @property
    def filename(self) -> str:
        if self.segment:
            return f"{self.schema_name}@{self.table_name}#{self.segment}.dat"
        return f"{self.schema_name}@{self.table_name}.dat"

    def load(self) -> None:
        path = os.path.join(self.folder, self.environ, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data source file {path} does not exist.")
        with open(path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def save(self) -> None:
        path = os.path.join(self.folder, self.environ, self.filename)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.data,
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )


class DataModel(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    schema_name: str
    table_name: str
    description: str
    layout: str
    settings: dict[str, SettingInfo]
    sync_mode: str
    value: str | None = None
    caption: str | None = None
    segment: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None

    @classmethod
    def load(cls, folder: str, environ: str, name: str):
        with open(os.path.join(folder, environ, name), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            **data
        )

    def save(self) -> None:
        filename = os.path.join(self.folder, self.environ, self.filename)
        with open(filename, 'w', encoding='utf-8') as f:
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
    def filename(self) -> str:
        return f"{self.schema_name}@{self.table_name}.yaml"

    @property
    def datasources(self):
        if not self.segment:
            yield DataSource(
                folder=self.folder,
                environ=self.environ,
                schema_name=self.schema_name,
                table_name=self.table_name,
            )

        for path in sorted(pathlib.Path(self.folder, self.environ, self.schema_name).glob(f"{self.schema_name}@{self.table_name}#*.dat")):
            seg = path.stem.split('#', 1)[1] if '#' in path.stem else None
            yield DataSource(
                folder=self.folder,
                environ=self.environ,
                schema_name=self.schema_name,
                table_name=self.table_name,
                segment=seg
            )


class DataModelManager:

    def __init__(self, folder: str, environ: str):
        self.folder = folder
        self.environ = environ

    def __getitem__(self, key: str) -> DataModel:
        return DataModel.load(self.folder, self.environ, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/*/*.yaml')):
            if path.name == '_mapping.yaml':
                continue
            name = str(path.parent.relative_to(pathlib.Path(self.folder) / self.environ))
            yield DataModel.load(self.folder, self.environ, name)

    def add(self, model: DataModel) -> None:
        filename = os.path.join(self.folder, self.environ, model.filename)
        if os.path.exists(filename):
            raise DBGearEntityExistsError(f'DataModel {model.filename} already exists in {self.folder}/{self.environ}')
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(
                model.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def remove(self, model: DataModel) -> None:
        filename = os.path.join(self.folder, self.environ, model.filename)
        try:
            os.remove(filename)
        except OSError as e:
            raise DBGearEntityRemovalError(f'Failed to remove DataModel {model.filename}: {e}')
