import pydantic
import yaml
import pathlib
import os

from typing import Any

from .base import BaseSchema


class SettingInfo(BaseSchema):
    type: str
    width: int | None = None
    environ: str | None = None
    schema_name: str | None = None
    table_name: str | None = None


class DataSource:
    folder: str
    environ: str
    name: str
    schema_name: str
    table_name: str
    segment: str | None = None
    data: list[dict[str, Any]]

    def __init__(self, folder: str, environ: str, name: str, schema_name: str, table_name: str, segment: str | None = None):
        self.folder = folder
        self.environ = environ
        self.name = name
        self.schema_name = schema_name
        self.table_name = table_name
        self.segment = segment
        self.data = []

    @property
    def filename(self) -> str:
        if self.segment:
            return f"{self.schema_name}@{self.table_name}#{self.segment}.dat"
        return f"{self.schema_name}@{self.table_name}.dat"

    def exists(self) -> bool:
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        return os.path.exists(path)

    def load(self) -> None:
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data source file {path} does not exist.")
        with open(path, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def save(self) -> None:
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.data,
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False
            )

    def remove(self) -> None:
        path = os.path.join(self.folder, self.environ, self.name, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data source file {path} does not exist.")
        os.remove(path)


class DataModel(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    map_name: str = pydantic.Field(exclude=True)
    schema_name: str = pydantic.Field(exclude=True)
    table_name: str = pydantic.Field(exclude=True)
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
    def load(cls, folder: str, environ: str, map_name: str, schema_name: str, table_name: str):
        with open(os.path.join(folder, environ, map_name, f'{schema_name}@{table_name}.yaml'), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            map_name=map_name,
            schema_name=schema_name,
            table_name=table_name,
            **data
        )

    def save(self) -> None:
        filename = os.path.join(self.folder, self.environ, self.map_name, self.filename)
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

    def remove(self) -> None:
        path = os.path.join(self.folder, self.environ, self.map_name, self.filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data model file {self.filename} does not exist.")

        for ds in self.datasources:
            path = os.path.join(self.folder, self.environ, self.map_name, ds.filename)
            if os.path.exists(path):
                os.remove(path)

        os.remove(path)

    @property
    def filename(self) -> str:
        return f"{self.schema_name}@{self.table_name}.yaml"

    @property
    def datasources(self):
        if not self.segment:
            yield DataSource(
                folder=self.folder,
                environ=self.environ,
                name=self.map_name,
                schema_name=self.schema_name,
                table_name=self.table_name,
            )

        for path in sorted(pathlib.Path(self.folder, self.environ, self.schema_name).glob(f"{self.schema_name}@{self.table_name}#*.dat")):
            seg = path.stem.split('#', 1)[1] if '#' in path.stem else None
            yield DataSource(
                folder=self.folder,
                environ=self.environ,
                name=self.map_name,
                schema_name=self.schema_name,
                table_name=self.table_name,
                segment=seg
            )
