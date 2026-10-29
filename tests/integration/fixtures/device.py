import pytest
from .yaml import load_yaml_resources


@pytest.fixture(scope="session")
def devices_list() -> list:
    return load_yaml_resources(kind="VISACloudDevice")


@pytest.fixture(scope="session")
def test_device(devices_list) -> dict:
    return devices_list[0]
