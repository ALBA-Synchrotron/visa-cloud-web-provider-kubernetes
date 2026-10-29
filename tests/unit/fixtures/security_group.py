import pytest


@pytest.fixture(scope="session")
def security_groups_list() -> list[dict]:
    return [
        {
            "metadata": {"name": "test-sec-group-1"},
        },
        {
            "metadata": {"name": "test-sec-group-2"},
        },
    ]
