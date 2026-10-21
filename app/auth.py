from typing import Any, Callable, TypeVar

from labels.common import ERR_API_AUTH_NOT_CONFIGURED, ERR_INVALID_API_KEY

import secrets
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar, cast

from flask import current_app, jsonify, request

F = TypeVar("F", bound=Callable[..., Any])


def authenticate_api_key():
    api_key: str | None = current_app.config["AUTH_API_KEY"]

    if not api_key:
        return jsonify({
            "error": ERR_API_AUTH_NOT_CONFIGURED,
        }), HTTPStatus.INTERNAL_SERVER_ERROR

    header_name: str = current_app.config["AUTH_API_KEY_HEADER_NAME"]
    provided_key: str = request.headers.get(header_name, "")

    if not secrets.compare_digest(provided_key, api_key):
        return jsonify({
            "error": ERR_INVALID_API_KEY,
        }), HTTPStatus.UNAUTHORIZED

    return None


def require_api_key(f: F) -> F:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        response = authenticate_api_key()

        if response is not None:
            return response

        return f(*args, **kwargs)

    return cast(F, decorated)
