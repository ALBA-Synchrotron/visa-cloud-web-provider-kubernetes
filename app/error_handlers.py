from http import HTTPStatus

from flask import jsonify, current_app, Flask
from flask.typing import ResponseReturnValue

from .labels.common import NOT_FOUND_SFX
from .utils.exceptions import KubernetesError, KubernetesNotFoundError


def handle_k8s_error(e: KubernetesError) -> ResponseReturnValue:
    current_app.logger.exception(e)
    return jsonify(error=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


def handle_k8s_not_found_errors(e: KubernetesNotFoundError) -> ResponseReturnValue:
    error_msg: str = f"{e.obj_type_name} with name={e.obj_name} {NOT_FOUND_SFX}"
    current_app.logger.error(error_msg)
    return jsonify(error=error_msg), HTTPStatus.NOT_FOUND


def register_error_handlers(app: Flask) -> None:
    app.register_error_handler(KubernetesError, handle_k8s_error)
    app.register_error_handler(KubernetesNotFoundError, handle_k8s_not_found_errors)
