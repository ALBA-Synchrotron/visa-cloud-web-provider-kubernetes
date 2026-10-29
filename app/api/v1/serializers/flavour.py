import orjson

from app.utils.helpers import convert_memory, to_cores


def flavour_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")
    limits: dict = spec.get("limits")

    return {
        "id": metadata.get("name"),
        "name": metadata.get("name"),
        "cpus": max(to_cores(limits.get("cpu")), 1),
        "disk": convert_memory(spec.get("diskSize")),
        "ram": convert_memory(limits.get("memory")),
    }


def flavours_to_json(flavours, dump: bool = True) -> bytes | dict | list:
    if isinstance(flavours, dict):
        return orjson.dumps(flavour_to_dict(flavours)) if dump else flavour_to_dict(flavours)
    return orjson.dumps([flavour_to_dict(f) for f in flavours]) if dump else [flavour_to_dict(f) for f in flavours]
