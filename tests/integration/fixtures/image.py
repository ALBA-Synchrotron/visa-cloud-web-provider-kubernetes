import pytest
from .yaml import load_yaml_resources


@pytest.fixture(scope="session")
def images_list() -> list:
    return load_yaml_resources(kind="VISACloudImage")


@pytest.fixture(scope="session")
def test_image(images_list) -> dict:
    return images_list[0]
