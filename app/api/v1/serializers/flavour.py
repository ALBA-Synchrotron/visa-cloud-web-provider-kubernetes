import orjson


def flavour_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")
    limits: dict = spec.get("limits")

    return {
        "id": metadata.get("name"),
        "name": metadata.get("name"),
        "cpus": limits.get("cpu"),
        "disk": spec.get("diskSize"),
        "ram": limits.get("memory"),
    }


def flavours_to_json(flavours) -> bytes:
    if isinstance(flavours, dict):
        return orjson.dumps(flavour_to_dict(flavours))
    return orjson.dumps([flavour_to_dict(f) for f in flavours])
