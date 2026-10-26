from http import HTTPStatus

from flask import Blueprint, current_app, Response

from app.api.v1.serializers.instance import instance_to_json

bp: Blueprint = Blueprint("instances", __name__)


@bp.get("/instances", endpoint="get_all")
def get_all_flavours() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instances: list = k8s.list_visa_cloud_instances()
    return Response(instance_to_json(k8s_instances),
                    status=HTTPStatus.OK,
                    mimetype="application/json")
