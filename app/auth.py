import secrets
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, TypeVar, cast

from flask import request, jsonify, current_app

from labels.common import ERR_API_AUTH_NOT_CONFIGURED, ERR_INVALID_API_KEY

F = TypeVar("F", bound=Callable[..., Any])


def require_api_key(f: F) -> F:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        api_key: str | None = current_app.config["AUTH_API_KEY"]

        if not api_key:
            return jsonify({
                "error": ERR_API_AUTH_NOT_CONFIGURED
            }), HTTPStatus.INTERNAL_SERVER_ERROR

        provided_key: str = request.headers.get(current_app.config["AUTH_API_KEY_HEADER_NAME"], "")

        if not secrets.compare_digest(provided_key, api_key):
            return jsonify({
                "error": ERR_INVALID_API_KEY
            }), HTTPStatus.UNAUTHORIZED

        return f(*args, **kwargs)

    return cast(F, decorated)
