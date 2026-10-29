from http import HTTPStatus, HTTPMethod

import pytest
from flask import current_app

ENDPOINT_NAME_PREFIX: str = "v1.instance"
INSTANCE_ENDPOINTS: list[tuple[str, dict, str]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_all", {}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_by_name", {"instance_id": "1"}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_ip_by_name", {"instance_id": "1"}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.start_instance", {"instance_id": "1"}, HTTPMethod.POST),
    (f"{ENDPOINT_NAME_PREFIX}.stop_instance", {"instance_id": "1"}, HTTPMethod.POST),
    (f"{ENDPOINT_NAME_PREFIX}.restart_instance", {"instance_id": "1"}, HTTPMethod.POST),
    (f"{ENDPOINT_NAME_PREFIX}.get_all_identifiers", {}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.get_security_groups_by_name", {"instance_id": "1"}, HTTPMethod.GET),
    (f"{ENDPOINT_NAME_PREFIX}.add_security_group", {"instance_id": "1"}, HTTPMethod.POST),
    (f"{ENDPOINT_NAME_PREFIX}.remove_security_group", {"instance_id": "1"}, HTTPMethod.POST),
    (f"{ENDPOINT_NAME_PREFIX}.delete_instance", {"instance_id": "1"}, HTTPMethod.DELETE),
    (f"{ENDPOINT_NAME_PREFIX}.create_instance", {}, HTTPMethod.POST),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs, allowed_method",
    INSTANCE_ENDPOINTS,
    ids=[e for e, _, _ in INSTANCE_ENDPOINTS],
)
def test_instance_endpoints_require_auth(app, client, endpoint, url_kwargs, allowed_method) -> None:
    with app.test_request_context():
        url = current_app.url_for(endpoint, **url_kwargs)
        response = client.open(url, method=allowed_method)
        assert response.status_code == HTTPStatus.UNAUTHORIZED
