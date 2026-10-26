import orjson


def security_group_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")

    return {
        "name": metadata.get("name"),
    }


def security_group_to_json(sec_groups) -> bytes:
    if isinstance(sec_groups, dict):
        return orjson.dumps(security_group_to_dict(sec_groups))
    return orjson.dumps([security_group_to_dict(f) for f in sec_groups])
