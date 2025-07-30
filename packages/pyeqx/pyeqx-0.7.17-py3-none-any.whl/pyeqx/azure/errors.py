from pyeqx.core.models.module import DataModule
from pyeqx.core.models.storage import Data


class StorageNotSupportedException(Exception):
    def __init__(self, storage: Data):
        self.storage = storage

    def __str__(self) -> str:
        return f"Storage: '{self.storage.type}' is not supported."


class ModuleNotSupportedException(Exception):
    def __init__(self, module: DataModule):
        self.module = module

    def __str__(self) -> str:
        return f"Module: '{self.module.type}' is not supported."


class AzureStorageException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
