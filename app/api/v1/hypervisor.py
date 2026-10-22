from http import HTTPStatus

from flask import Blueprint, Response
from orjson import orjson

bp: Blueprint = Blueprint("hypervisor", __name__)


@bp.get("/custom_resource_classes", endpoint="get_custom_resource_classes")
def get_all_custom_resource_classes() -> Response:
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/hypervisor_inventories", endpoint="get_hypervisor_inventories")
def get_all_hypervisor_inventories() -> Response:
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/hypervisor_usages", endpoint="get_hypervisor_usages")
def get_all_hypervisor_usages() -> Response:
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/hypervisor_allocations", endpoint="get_hypervisor_allocations")
def get_all_hypervisor_allocations() -> Response:
    # TODO: This returns an empty list while there is no support for this function in the visa-k8s provider.
    return Response(orjson.dumps([]),
                    status=HTTPStatus.OK,
                    mimetype="application/json")
