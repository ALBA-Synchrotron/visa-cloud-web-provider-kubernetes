import orjson


def instance_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")
    status: dict = f.get("status")

    return {
        "id": metadata.get("uid"),
        "name": metadata.get("name"),
        "state": status.get("state"),
        "flavourId": spec.get("flavour").get("name"),
        "imageId": spec.get("image").get("name"),
        "createdAt": metadata.get("creationTimestamp"),
        "address": metadata.get("address", None),
        "securityGroups": [i.get("name") for i in spec.get("securityGroups")],
        "fault": {
            "message": "",
            "code": "",
            "details": "",
            "createdAt": ""
        }
    }


def instance_to_json(instances) -> bytes:
    if isinstance(instances, dict):
        return orjson.dumps(instance_to_dict(instances))
    return orjson.dumps([instance_to_dict(f) for f in instances])
