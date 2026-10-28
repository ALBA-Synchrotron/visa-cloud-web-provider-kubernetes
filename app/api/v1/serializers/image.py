import orjson

from utils.helpers import convert_memory


def image_to_dict(f) -> dict:
    metadata: dict = f.get("metadata")
    spec: dict = f.get("spec")

    return {
        "id": metadata.get("name"),
        "name": metadata.get("name"),
        "size": convert_memory(spec.get("size") or 1),
        "createdAt": metadata.get("creationTimestamp"),
    }


def images_to_json(images) -> bytes:
    if isinstance(images, dict):
        return orjson.dumps(image_to_dict(images))
    return orjson.dumps([image_to_dict(f) for f in images])
