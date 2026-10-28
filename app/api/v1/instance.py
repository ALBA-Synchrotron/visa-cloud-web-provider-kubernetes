from http import HTTPStatus

import orjson
from flask import Blueprint, current_app, Response, request

from app.api.v1.serializers.instance import instance_to_json, validate_security_group_name_payload, \
    validate_instance_payload
from app.labels.common import MSG_START_INSTANCE, MSG_STOP_INSTANCE, MSG_REBOOT_INSTANCE, MSG_SEC_GROUP_ADDED, \
    MSG_SEC_GROUP_REMOVED, MSG_INSTANCE_DELETED

bp: Blueprint = Blueprint("instance", __name__)


@bp.get("/instances", endpoint="get_all")
def get_all_instances() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instances: list = k8s.list_visa_cloud_instances()
    return Response(instance_to_json(k8s_instances),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/instances/<instance_id>", endpoint="get_by_name")
def get_instance_by_name(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instances: list = k8s.get_visa_cloud_instance(instance_id)
    return Response(instance_to_json(k8s_instances),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/instances/<instance_id>/ip", endpoint="get_ip_by_name")
def get_instance_ip_by_name(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instances: list = k8s.get_visa_cloud_instance(instance_id)
    return Response(instance_to_json(k8s_instances, only_address=True),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances/<instance_id>/start", endpoint="start_instance")
def start_instance(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s.start_visa_cloud_instance(instance_id)
    return Response(orjson.dumps({"message": f"{MSG_START_INSTANCE} name={instance_id}"}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances/<instance_id>/shutdown", endpoint="stop_instance")
def stop_instance(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s.stop_visa_cloud_instance(instance_id)
    return Response(orjson.dumps({"message": f"{MSG_STOP_INSTANCE} name={instance_id}"}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances/<instance_id>/reboot", endpoint="restart_instance")
def restart_instance(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s.restart_visa_cloud_instance(instance_id)
    return Response(orjson.dumps({"message": f"{MSG_REBOOT_INSTANCE} name={instance_id}"}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/instances/identifiers", endpoint="get_all_identifiers")
def get_all_instances_identifiers() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instances: list = k8s.list_visa_cloud_instances()
    return Response(instance_to_json(k8s_instances, only_id=True),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/instances/<instance_id>/security_groups", endpoint="get_security_groups_by_name")
def get_instance_security_groups_by_name(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_instance: list = k8s.get_visa_cloud_instance(instance_id)
    return Response(instance_to_json(k8s_instance, only_sec_groups=True),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances/<instance_id>/security_groups", endpoint="add_security_group")
def add_instance_security_group(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    body: dict = request.get_json()
    validate_security_group_name_payload(body)

    k8s.add_security_group_to_instance(instance_id, body.get("name"))
    return Response(orjson.dumps({"message": MSG_SEC_GROUP_ADDED}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances/<instance_id>/security_groups/remove", endpoint="remove_security_group")
def remove_instance_security_group(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    body: dict = request.get_json()
    validate_security_group_name_payload(body)

    k8s.remove_security_group_to_instance(instance_id, body.get("name"))
    return Response(orjson.dumps({"message": MSG_SEC_GROUP_REMOVED}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.delete("/instances/<instance_id>", endpoint="delete_instance")
def delete_instance(instance_id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s.delete_visa_cloud_instance(instance_id)
    return Response(orjson.dumps({"message": MSG_INSTANCE_DELETED}),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.post("/instances", endpoint="create_instance")
def create_instance() -> Response:
    k8s = current_app.extensions["kubernetes"]
    body: dict = request.get_json()
    validate_instance_payload(body)

    k8s_instance: object = k8s.create_visa_cloud_instance(body)
    return Response(instance_to_json(k8s_instance),
                    status=HTTPStatus.CREATED,
                    mimetype="application/json")
