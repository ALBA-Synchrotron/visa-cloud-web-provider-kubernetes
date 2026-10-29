import orjson
from flask import current_app

from app.utils.exceptions import InvalidPayloadFormat
from app.labels.kubernetes import CLOUD_PROVIDER_PREFIX


def instance_to_dict(f, only_address: bool = False, only_id: bool = False,
                     only_sec_groups: bool = False) -> dict | list:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")
    status: dict = f.get("status", {})
    fault: dict = status.get("error", {})

    if only_address:
        return {"address": metadata.get("address", ""), "id": metadata.get("name")}

    if only_id:
        return {"id": metadata.get("name")}

    if only_sec_groups:
        return [i.get("name") for i in spec.get("securityGroups", [])]

    return {
        "id": metadata.get("name"),
        "name": metadata.get("labels").get(f"{CLOUD_PROVIDER_PREFIX}/visa-name"),
        "state": status.get("state", "STARTING"),
        "flavourId": spec.get("flavour").get("name"),
        "imageId": spec.get("image").get("name"),
        "createdAt": metadata.get("creationTimestamp"),
        "address": status.get("address", None),
        "securityGroups": [i.get("name") for i in spec.get("securityGroups", [])],
        "fault": {
            "message": fault.get("message", ""),
            "code": fault.get("code", 0),
            "details": fault.get("details", ""),
            "createdAt": fault.get("createdAt", ""),
        }
    }


def instance_to_json(instances, only_address: bool = False, only_id: bool = False,
                     only_sec_groups: bool = False, creation_request: bool = False) -> bytes:
    if isinstance(instances, dict):
        return orjson.dumps(
            instance_to_dict(instances, only_address=only_address, only_id=only_id, only_sec_groups=only_sec_groups))
    return orjson.dumps(
        [instance_to_dict(f, only_address=only_address, only_id=only_id, only_sec_groups=only_sec_groups) for f in
         instances])


def validate_security_group_name_payload(payload: dict) -> None:
    if "name" not in payload or not isinstance(payload["name"], str):
        raise InvalidPayloadFormat()


def validate_instance_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise InvalidPayloadFormat()

    expected_fields: dict = {
        "name": str,
        "imageId": str,
        "flavourId": str,
        "securityGroups": list,
        "metadata": dict,
    }

    for field, expected_type in expected_fields.items():
        if (
                field not in payload
                or not isinstance(payload[field], expected_type)
        ):
            raise InvalidPayloadFormat()

    if (
            "bootCommand" in payload
            and not isinstance(payload["bootCommand"], str)
    ):
        raise InvalidPayloadFormat()

    if not all(
            isinstance(group, str)
            for group in payload["securityGroups"]
    ):
        raise InvalidPayloadFormat()

    metadata: dict = payload["metadata"]

    if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in metadata.items()
    ):
        raise InvalidPayloadFormat()


def get_k8s_instance_body_from_payload(payload: dict) -> dict:
    metadata: dict = payload.get("metadata")
    initial_state: str = "ACTIVE" if current_app.config["AUTO_START_INSTANCES_ON_CREATION"] else "STOPPED"

    return {
        "apiVersion": f"{CLOUD_PROVIDER_PREFIX}/v1",
        "kind": "VISACloudInstance",
        "metadata": {
            "name": str(metadata.get("id")),
            "namespace": current_app.config["K8S_NAMESPACE"],
            "labels": {
                f"{CLOUD_PROVIDER_PREFIX}/visa-name": payload.get("name"),
                f"{CLOUD_PROVIDER_PREFIX}/id": metadata.get("id"),
                f"{CLOUD_PROVIDER_PREFIX}/uid": metadata.get("uid"),
            },
            "annotations": {
                f"{CLOUD_PROVIDER_PREFIX}/owner": metadata.get("owner"),
                f"{CLOUD_PROVIDER_PREFIX}/pamPublicKey": metadata.get("pamPublicKey"),
                f"{CLOUD_PROVIDER_PREFIX}/proposals": metadata.get("proposals", []),
                f"{CLOUD_PROVIDER_PREFIX}/screenWidth": metadata.get("screenWidth"),
                f"{CLOUD_PROVIDER_PREFIX}/screenHeight": metadata.get("screenHeight"),
                f"{CLOUD_PROVIDER_PREFIX}/keyboardLayout": metadata.get("keyboardLayout"),
                f"{CLOUD_PROVIDER_PREFIX}/instruments": metadata.get("instruments"),
                f"{CLOUD_PROVIDER_PREFIX}/bootCommand": payload.get("instruments"),
            }
        },
        "spec": {
            "associatedProposals": metadata.get("proposals").split(",") or [],
            "desiredState": initial_state,
            "flavour": {"name": payload.get("flavourId")},
            "image": {"name": payload.get("imageId")},
            "securityGroups": [
                {"name": i} for i in payload.get("securityGroups", [])
            ]
        }
    }
