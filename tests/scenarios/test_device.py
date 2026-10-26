from http import HTTPStatus

import pytest
from flask import current_app, url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.device"
DEVICE_ENDPOINTS: list[tuple[str, dict]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_all", {}),
    (f"{ENDPOINT_NAME_PREFIX}.get_device_filtered", {"device_type": "VIRTUAL_GPU", "device_identifier": "VGPU"}),
    (f"{ENDPOINT_NAME_PREFIX}.get_device_allocations", {}),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs",
    DEVICE_ENDPOINTS,
    ids=[e for e, _ in DEVICE_ENDPOINTS]
)
def test_device_endpoints_require_auth(app, client, endpoint, url_kwargs) -> None:
    with app.test_request_context():
        response = client.get(current_app.url_for(endpoint, **url_kwargs))
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_all_devices(app, client, api_key_authentication, devices_list) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_all"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
        for i in r_data:
            assert isinstance(i, dict)
            assert all(
                key in i.keys()
                for key in ["identifier", "name", "type"]
            )
        assert len(devices_list) == len(r_data)


def test_get_filtered_device(app, client, api_key_authentication, test_device) -> None:
    test_device_identifier: str = test_device.get("spec").get("identifier")
    test_device_type: str = test_device.get("spec").get("type")

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_device_filtered",
                                             device_type=test_device_type, device_identifier=test_device_identifier),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in ["identifier", "type"]
        )
        assert r_data["identifier"] == test_device_identifier
        assert r_data["type"] == test_device_type


def test_get_non_existent_filtered_device(app, client, api_key_authentication) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_device_filtered",
                                             device_type="GPU-ccino", device_identifier="octopus"),
                                     headers=api_key_authentication)

        assert r.status_code == HTTPStatus.NOT_FOUND


def test_get_device_allocations(app, client, api_key_authentication) -> None:
    # TODO: Since there is no support for this function in the visa-k8s provider, this tests that the API's response
    #       is acceptable to the VISA API server.
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_device_allocations"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)

