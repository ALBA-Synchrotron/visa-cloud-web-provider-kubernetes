import pytest


@pytest.fixture(scope="session")
def images_list() -> list[dict]:
    return [
        {
            "metadata": {"name": "test-image-1", "creationTimestamp": "2026-10-08T10:04:12Z"},
            "spec": {
                "size": "723.2Mi",
            },
        },
        {
            "metadata": {"name": "test-image-2", "creationTimestamp": "2026-10-08T10:04:12Z"},
            "spec": {
                "size": "221.2Mi",
            },
        },
    ]

@pytest.fixture(scope="session")
def test_image(images_list) -> dict:
    return images_list[0]
