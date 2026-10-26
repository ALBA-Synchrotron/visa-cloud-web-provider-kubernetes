import pytest


@pytest.fixture
def images_list():
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

@pytest.fixture
def test_image(images_list):
    return images_list[0]
