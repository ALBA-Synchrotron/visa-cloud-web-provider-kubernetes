from http import HTTPStatus

from flask import Blueprint, current_app, Response
from orjson import orjson

from app.api.v1.serializers.flavour import flavours_to_json

bp: Blueprint = Blueprint("flavour", __name__)


@bp.get("/flavours", endpoint="get_all")
def get_all_flavours() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_flavours: list = k8s.list_visa_cloud_flavours()
    return Response(flavours_to_json(k8s_flavours),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/flavours/<id>", endpoint="get_by_name")
def get_flavour_by_name(id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_flavour: list = k8s.get_visa_cloud_flavour(id)
    return Response(flavours_to_json(k8s_flavour),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/flavours/<id>/device_allocations", endpoint="get_device_allocation_by_flavour_name")
def get_device_allocation_by_flavour_name(id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    _: list = k8s.get_visa_cloud_flavour(id)
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]), status=HTTPStatus.OK, mimetype="application/json")
