import orjson


def security_group_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")

    return {
        "name": metadata.get("name"),
    }


def security_group_to_json(flavours) -> bytes:
    if isinstance(flavours, dict):
        return orjson.dumps(security_group_to_dict(flavours))
    return orjson.dumps([security_group_to_dict(f) for f in flavours])
