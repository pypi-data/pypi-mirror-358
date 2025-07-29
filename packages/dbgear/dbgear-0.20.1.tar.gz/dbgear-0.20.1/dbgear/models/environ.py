import pydantic
import yaml
import pathlib
import os

from .base import BaseSchema
from .schema import SchemaManager
from .mapping import MappingManager
from .tenant import TenantRegistry
from .option import DBGearOptions
from .exceptions import DBGearEntityExistsError
from .exceptions import DBGearEntityNotFoundError
from .exceptions import DBGearEntityRemovalError


class Environ(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    description: str
    deployment: dict[str, str] = {}
    options: DBGearOptions | None = None

    _schemas: SchemaManager | None = None
    _tenant: TenantRegistry | None = None

    @classmethod
    def load(cls, folder: str, name: str) -> None:
        with open(f'{folder}/{name}/environ.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            name=name,
            **data)

    @property
    def schemas(self) -> SchemaManager | None:
        if self._schemas is None:
            self._schemas = SchemaManager.load(f'{self.folder}/{self.name}/schema.yaml')
        return self._schemas

    @property
    def tenant(self) -> TenantRegistry | None:
        if self._tenant is None:
            self._tenant = TenantRegistry.load(self.folder, self.name)
        return self._tenant

    @property
    def mappings(self) -> MappingManager:
        return MappingManager(self.folder, self.name)

    @property
    def databases(self):
        for map in self.mappings:
            if map.deploy:
                yield map

        yield from self.tenant.materialize()


class EnvironManager:

    def __init__(self, folder: str):
        self.folder = folder

    def __getitem__(self, key: str) -> Environ:
        return Environ.load(self.folder, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob('*/environ.yaml')):
            name = str(path.parent.relative_to(self.folder))
            yield Environ.load(self.folder, name)

    def add(self, environ: Environ) -> None:
        path = os.path.join(self.folder, environ.name)
        if os.path.exists(path):
            raise DBGearEntityExistsError(f'Environment {environ.name} already exists in {self.folder}')

        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, 'environ.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(environ.model_dump(
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
        path = os.path.join(self.folder, name)
        if not os.path.exists(path):
            raise DBGearEntityNotFoundError(f'Environment {name} does not exist in {self.folder}')
        files = [f for f in os.listdir(path) if f != 'environ.yaml']
        if files:
            raise DBGearEntityRemovalError(f'Cannot remove {path}: files other than environ.yaml exist')
        os.remove(os.path.join(path, 'environ.yaml'))
        os.rmdir(path)


if __name__ == '__main__':
    # Example usage
    envs = EnvironManager('../../etc/test')
    for environ in envs:
        print(environ)

    # envs.remove('env2')
