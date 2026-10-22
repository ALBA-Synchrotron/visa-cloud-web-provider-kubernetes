import orjson


def image_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")

    return {
        "id": metadata.get("name"),
        "name": metadata.get("name"),
        "size": spec.get("size"),
        "createdAt": metadata.get("creationTimestamp"),
    }


def images_to_json(flavours) -> bytes:
    if isinstance(flavours, dict):
        return orjson.dumps(image_to_dict(flavours))
    return orjson.dumps([image_to_dict(f) for f in flavours])
