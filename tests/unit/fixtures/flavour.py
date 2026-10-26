import pytest


@pytest.fixture(scope="session")
def flavours_list() -> list[dict]:
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

@pytest.fixture(scope="session")
def test_flavour(flavours_list) -> dict:
    return flavours_list[0]