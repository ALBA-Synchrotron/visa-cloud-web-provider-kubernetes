import pytest


@pytest.fixture(scope="session")
def devices_list() -> list[dict]:
    return [
        {
            "metadata": {"name": "test-flavour-1"},
            "spec": {
                "identifier": "VGPU",
                "type": "VIRTUAL_GPU",
            },
        },
        {
            "metadata": {"name": "test-flavour-2"},
            "spec": {
                "identifier": "a100",
                "type": "PCI_PASSTHROUGH",
            },
        },
    ]

@pytest.fixture(scope="session")
def test_device(devices_list) -> dict:
    return devices_list[0]