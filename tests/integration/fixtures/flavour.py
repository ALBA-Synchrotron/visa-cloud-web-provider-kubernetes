import pytest
from .yaml import load_yaml_resources


@pytest.fixture(scope="session")
def flavours_list() -> list:
    return load_yaml_resources(kind="VISACloudFlavour")


@pytest.fixture(scope="session")
def test_flavour(flavours_list) -> dict:
    return flavours_list[0]
