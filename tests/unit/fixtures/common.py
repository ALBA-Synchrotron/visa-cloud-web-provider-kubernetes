from http import HTTPStatus
from typing import Any, Generator

import pytest
from flask import Flask, jsonify
from flask.testing import FlaskClient
from flask.typing import ResponseReturnValue

from app import create_app
from app.auth import require_api_key
from app.config import UnitTestConfig


@pytest.fixture(scope="session")
def app(dummy_kubernetes_extension) -> Generator[Flask, Any, None]:
    app = create_app(UnitTestConfig())

    @app.get("/protected", endpoint="test_protected")
    @require_api_key
    def protected_endpoint() -> ResponseReturnValue:
        return jsonify({"status": "ok"}), HTTPStatus.OK

    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def api_key_authentication(app) -> dict:
    header_name: str = app.config["AUTH_API_KEY_HEADER_NAME"]
    api_key: str = app.config["AUTH_API_KEY"]
    return {header_name: api_key}