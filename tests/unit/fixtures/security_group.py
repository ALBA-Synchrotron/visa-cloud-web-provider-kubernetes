import pytest


@pytest.fixture
def security_groups_list():
    return [
        {
            "metadata": {"name": "test-sec-group-1"},
        },
        {
            "metadata": {"name": "test-sec-group-2"},
        },
    ]
