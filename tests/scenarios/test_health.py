from http import HTTPStatus

from flask import url_for
from werkzeug.test import TestResponse

from app import ALL_COOLIO


def test_healthz_returns_ok(app, client) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for("healthz"))

        assert r.status_code == HTTPStatus.OK
        assert r.get_json() == {"status": ALL_COOLIO}
