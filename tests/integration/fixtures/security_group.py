import pytest
from .yaml import load_yaml_resources

@pytest.fixture(scope="session")
def security_groups_list() -> list:
    return load_yaml_resources(kind="VISACloudSecurityGroup")
