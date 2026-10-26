from http import HTTPStatus

from flask import url_for


def test_valid_api_key(app, client, api_key_authentication) -> None:
    with app.test_request_context():
        r = client.get(url_for("test_protected"), headers={**api_key_authentication})

        assert r.status_code == HTTPStatus.OK


def test_invalid_api_key(app, client) -> None:
    with app.test_request_context():
        with app.test_request_context():
            r = client.get(url_for("test_protected"))

        assert r.status_code == HTTPStatus.UNAUTHORIZED
