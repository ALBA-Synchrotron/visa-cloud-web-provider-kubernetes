from http import HTTPStatus, HTTPMethod

import pytest
from flask import current_app, url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.metrics"
IMAGE_ENDPOINTS: list[tuple[str, dict, str]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_all", {}, HTTPMethod.GET),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs, allowed_method",
    IMAGE_ENDPOINTS,
    ids=[e for e, _, _ in IMAGE_ENDPOINTS]
)
def test_metrics_endpoints_require_auth(app, client, endpoint, url_kwargs, allowed_method) -> None:
    with app.test_request_context():
        url = current_app.url_for(endpoint, **url_kwargs)
        response = client.open(url, method=allowed_method)
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_all_metrics(app, client, api_key_authentication, instances_list) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_all"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in ["maxTotalRamSize", "totalRamUsed", "totalInstancesUsed", "maxTotalInstances", "maxTotalCores",
                        "totalCoresUsed"]
        )

        assert r_data.get("totalInstancesUsed") == len(instances_list)
