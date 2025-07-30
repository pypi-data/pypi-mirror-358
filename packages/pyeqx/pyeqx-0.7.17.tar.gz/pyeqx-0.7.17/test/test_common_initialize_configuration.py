from typing import Any
from unittest import TestCase


class TestCommonInitializeConfiguration(TestCase):
    raw_config: dict[str, Any]

    @classmethod
    def setUpClass(self):
        self.raw_config = {
            "engine": {
                "storage": "system",
                "tmpPath": "/home/jovyan/tmp/",
                "isDedicatedSpark": False,
                "sparkExecutorCore": 1,
                "sparkExecutorMemory": "1g",
                "sparkEndpoint": "spark://localhost:7077",
                "isDynamicAllocation": True,
                "sparkExecutorMinInstances": 1,
                "sparkExecutorMaxInstances": 1,
            }
        }
        return super().setUpClass()

    @classmethod
    def tearDownClass(self):
        return super().tearDownClass()

    def test_initialize_configuration_with_data_module_file_type_should_success(self):
        pass
