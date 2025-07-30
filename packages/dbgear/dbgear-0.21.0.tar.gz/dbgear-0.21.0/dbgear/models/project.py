# from importlib import import_module
import pydantic
import yaml

from .base import BaseSchema
from .schema import SchemaManager
from .environ import EnvironManager
from .option import DBGearOptions


# class Binding(BaseSchema):
#     type: str
#     value: str


class Project(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    project_name: str
    description: str
    options: DBGearOptions = pydantic.Field(default_factory=DBGearOptions)

    _schemas: SchemaManager | None = None

    # def __init__(self, folder: str, data: dict):
    #     self.folder = folder
    #     self.schemas = SchemaManager.load(f'{folder}/schema.yaml')
    #     self.project_name = data['project_name']
    #     self.description = data['description']
    # self._definitions = data.get('definitions', [])
    # self._rules = data['rules']
    # self._bindings = {k: Binding(**v) for k, v in data['bindings'].items()}
    # self.deployments = data['deployments']

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

    # @property
    # def bindings(self) -> dict[str, Binding]:
    #     return self._bindings

    # @property
    # def rules(self) -> dict[str, str]:
    #     return self._rules

    # @property
    # def schemas(self) -> SchemaManager:
    #     return self._schemas

    # @property
    # def instances(self) -> list[str]:
    #     return list(self.schemas.get_schemas().keys())

    # def read_definitions(self) -> None:
    #     for items in self._definitions:
    #         self.logger.info(f"definition: {items['type']}")
    #         module = import_module(f'.{items["type"]}', 'dbgear.core.definitions')
    #         result = module.retrieve(self.folder, **items)

    #         self._schemas.update(result)


# def project(request) -> Project:
#     return request.app.state.project
