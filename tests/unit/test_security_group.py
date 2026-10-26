from http import HTTPStatus

import pytest
from flask import current_app, url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.security_group"
IMAGE_ENDPOINTS: list[tuple[str, dict]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_all", {}),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs",
    IMAGE_ENDPOINTS,
    ids=[e for e, _ in IMAGE_ENDPOINTS]
)
def test_security_group_endpoints_require_auth(app, client, endpoint, url_kwargs):
    with app.test_request_context():
        response = client.get(current_app.url_for(endpoint, **url_kwargs))
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_all_security_groups(app, client, api_key_authentication):
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
                for key in ["name"]
            )