import orjson


def device_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")

    return {
        "name": metadata.get("name"),
        "identifier": spec.get("identifier"),
        "type": spec.get("type"),
    }


def devices_to_json(devices) -> bytes:
    if isinstance(devices, dict):
        return orjson.dumps(device_to_dict(devices))
    return orjson.dumps([device_to_dict(f) for f in devices])
