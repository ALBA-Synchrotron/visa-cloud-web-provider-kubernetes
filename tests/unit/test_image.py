from http import HTTPStatus

import pytest
from flask import current_app, url_for
from werkzeug.test import TestResponse

from tests.unit.fixtures.image import DUMMY_IMAGES

ENDPOINT_NAME_PREFIX: str = "v1.image"
IMAGE_ENDPOINTS: list[tuple[str, dict]] = [
    (f"{ENDPOINT_NAME_PREFIX}.get_all", {}),
    (f"{ENDPOINT_NAME_PREFIX}.get_by_name", {"id": "1"}),
]


@pytest.mark.parametrize(
    "endpoint, url_kwargs",
    IMAGE_ENDPOINTS,
    ids=[e for e, _ in IMAGE_ENDPOINTS]
)
def test_image_endpoints_require_auth(app, client, endpoint, url_kwargs):
    with app.test_request_context():
        response = client.get(current_app.url_for(endpoint, **url_kwargs))
        assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_all_images(app, client, api_key_authentication):
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
                for key in ["id", "name", "size", "createdAt"]
            )


def test_get_image_by_id(app, client, api_key_authentication):
    test_image: dict = DUMMY_IMAGES[0]
    test_image_name: str = test_image.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             id=test_image_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in ["id", "name", "size", "createdAt"]
        )
        assert r_data["id"] == test_image_name


def test_get_non_existent_image_by_id(app, client, api_key_authentication):
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             id="non-existent-image"),
                                     headers=api_key_authentication)

        assert r.status_code == HTTPStatus.NOT_FOUND
