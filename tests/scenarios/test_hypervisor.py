from http import HTTPStatus, HTTPMethod

import pytest
from flask import current_app

ENDPOINT_NAME_PREFIX: str = "v1.hypervisor"
HYPERVISOR_ENDPOINTS: list[tuple[str, dict, str]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_custom_resource_classes", {}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_inventories", {}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_usages", {}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_allocations", {}, HTTPMethod.GET),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs, allowed_method",
    HYPERVISOR_ENDPOINTS,
    ids=[e for e, _, _ in HYPERVISOR_ENDPOINTS]
)
def test_hypervisor_endpoints_require_auth(app, client, endpoint, url_kwargs, allowed_method) -> None:
    with app.test_request_context():
        url = current_app.url_for(endpoint, **url_kwargs)
        response = client.open(url, method=allowed_method)
        assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    "endpoint, url_kwargs, allowed_method",
    HYPERVISOR_ENDPOINTS,
    ids=[e for e, _, _ in HYPERVISOR_ENDPOINTS]
)
def test_hypervisor_endpoints_acceptable_response(app, client, endpoint, url_kwargs,
                                                  api_key_authentication, allowed_method) -> None:
    # TODO: Since there is no support for this function in the visa-k8s provider, this tests that the API's response
    #       is acceptable to the VISA API server.
    with app.test_request_context():
        r = client.open(current_app.url_for(endpoint, **url_kwargs), headers=api_key_authentication,
                        method=allowed_method)
        r_data = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
