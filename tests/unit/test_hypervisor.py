from http import HTTPStatus

import pytest
from flask import current_app, url_for
from werkzeug.test import TestResponse

from fixtures.flavour import DUMMY_FLAVOURS

ENDPOINT_NAME_PREFIX: str = "v1.hypervisor"
HYPERVISOR_ENDPOINTS: list[tuple[str, dict]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_custom_resource_classes", {}),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_inventories", {}),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_usages", {}),
    (f"{ENDPOINT_NAME_PREFIX}.get_hypervisor_allocations", {}),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs",
    HYPERVISOR_ENDPOINTS,
    ids=[e for e, _ in HYPERVISOR_ENDPOINTS]
)
def test_hypervisor_endpoints_require_auth(app, client, endpoint, url_kwargs):
    with app.test_request_context():
        response = client.get(current_app.url_for(endpoint, **url_kwargs))
        assert response.status_code == HTTPStatus.UNAUTHORIZED



@pytest.mark.parametrize(
    "endpoint, url_kwargs",
    HYPERVISOR_ENDPOINTS,
    ids=[e for e, _ in HYPERVISOR_ENDPOINTS]
)
def test_hypervisor_endpoints_acceptable_response(app, client, endpoint, url_kwargs,
                                                  api_key_authentication):
    # TODO: Since there is no support for this function in the visa-k8s provider, this tests that the API's response
    #       is acceptable to the VISA API server.
    with app.test_request_context():
        r = client.get(current_app.url_for(endpoint, **url_kwargs), headers=api_key_authentication)
        r_data = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)