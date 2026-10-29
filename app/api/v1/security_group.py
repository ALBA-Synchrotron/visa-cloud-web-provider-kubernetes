from http import HTTPStatus

from flask import Blueprint, current_app, Response

from app.api.v1.serializers.security_group import security_group_to_json

bp: Blueprint = Blueprint("security_group", __name__)


@bp.get("/security_groups", endpoint="get_all")
def get_all_security_groups() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_sec_groups: list = k8s.list_visa_cloud_security_groups()
    return Response(security_group_to_json(k8s_sec_groups),
                    status=HTTPStatus.OK,
                    mimetype="application/json")
