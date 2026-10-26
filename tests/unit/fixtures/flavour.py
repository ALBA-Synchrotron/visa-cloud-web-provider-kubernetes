import pytest


@pytest.fixture
def flavours_list():
    return [
        {
            "metadata": {"name": "test-flavour-1"},
            "spec": {
                "diskSize": "10Gi",
                "limits": {"cpu": "1", "memory": "1Gi"},
            },
        },
        {
            "metadata": {"name": "test-flavour-2"},
            "spec": {
                "diskSize": "10Gi",
                "limits": {"cpu": "1", "memory": "1Gi"},
            },
        },
    ]

@pytest.fixture
def test_flavour(flavours_list):
    return flavours_list[0]