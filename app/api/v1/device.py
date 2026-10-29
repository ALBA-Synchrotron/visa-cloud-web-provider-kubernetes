from http import HTTPStatus

import orjson
from flask import Blueprint, current_app, Response

from app.api.v1.serializers.device import devices_to_json

bp: Blueprint = Blueprint("device", __name__)


@bp.get("/devices", endpoint="get_all")
def get_all_devices() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_devices: list = k8s.list_visa_cloud_devices()
    return Response(devices_to_json(k8s_devices),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/device/<device_type>/<device_identifier>", endpoint="get_device_filtered")
def get_device_filtered(device_type: str, device_identifier: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_device: dict = k8s.get_filtered_visa_cloud_device(device_type, device_identifier)
    return Response(devices_to_json(k8s_device),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/device_allocations", endpoint="get_device_allocations")
def get_all_device_allocations() -> Response:
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]),
                    status=HTTPStatus.OK,
                    mimetype="application/json")