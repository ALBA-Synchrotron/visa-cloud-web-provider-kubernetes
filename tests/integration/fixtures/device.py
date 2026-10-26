import pytest
from .yaml import load_yaml_resources


@pytest.fixture(scope="session")
def devices_list():
    return load_yaml_resources(kind="VISACloudDevice")


@pytest.fixture(scope="session")
def test_device(devices_list):
    return devices_list[0]
