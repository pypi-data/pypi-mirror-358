from typing import Type

from pyeqx.core.models import AppData


class ExecuteParameters:
    def __init__(self, name: str, cls: Type[AppData]):
        self.name = name
        self.cls = cls
