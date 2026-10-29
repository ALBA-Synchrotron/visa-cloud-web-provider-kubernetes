from http import HTTPStatus

from flask import jsonify, current_app, Flask
from flask.typing import ResponseReturnValue

from app.labels.common import NOT_FOUND_SFX, NOT_FOUND_IN_SFX, INVALID_PAYLOAD, CP_CREATION_QUOTA_EXCEEDED
from app.utils.exceptions import KubernetesError, KubernetesNotFoundError, KubernetesNotFoundInInstanceError, \
    InvalidPayloadFormat, CloudProviderResourceQuotaExceeded


def handle_k8s_error(e: KubernetesError) -> ResponseReturnValue:
    current_app.logger.exception(e)
    return jsonify(error=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


def handle_k8s_not_found_in_instance_error(e: KubernetesNotFoundInInstanceError) -> ResponseReturnValue:
    error_msg: str = f"{e.obj_type_name} with name={e.obj_name} {NOT_FOUND_IN_SFX} {e.obj_type_recipient_name} with name={e.obj_recipient_name}"
    current_app.logger.error(error_msg)
    return jsonify(error=error_msg), HTTPStatus.NOT_FOUND


def handle_k8s_not_found_error(e: KubernetesNotFoundError) -> ResponseReturnValue:
    error_msg: str = f"{e.obj_type_name} with name={e.obj_name} {NOT_FOUND_SFX}"
    current_app.logger.error(error_msg)
    return jsonify(error=error_msg), HTTPStatus.NOT_FOUND


def handle_invalid_payload_format_error(_: InvalidPayloadFormat) -> ResponseReturnValue:
    error_msg: str = INVALID_PAYLOAD
    current_app.logger.error(error_msg)
    return jsonify(error=error_msg), HTTPStatus.BAD_REQUEST


def handle_resource_quota_exceedance_error(_: CloudProviderResourceQuotaExceeded) -> ResponseReturnValue:
    error_msg: str = CP_CREATION_QUOTA_EXCEEDED
    current_app.logger.error(error_msg)
    return jsonify(error=error_msg), HTTPStatus.CONFLICT


def register_error_handlers(app: Flask) -> None:
    app.register_error_handler(KubernetesError, handle_k8s_error)
    app.register_error_handler(KubernetesNotFoundInInstanceError, handle_k8s_not_found_in_instance_error)
    app.register_error_handler(KubernetesNotFoundError, handle_k8s_not_found_error)
    app.register_error_handler(InvalidPayloadFormat, handle_invalid_payload_format_error)
    app.register_error_handler(CloudProviderResourceQuotaExceeded, handle_resource_quota_exceedance_error)
