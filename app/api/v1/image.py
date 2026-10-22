from http import HTTPStatus

from flask import Blueprint, current_app, Response

from v1.serializers.image import images_to_json

bp: Blueprint = Blueprint("image", __name__)


@bp.get("/images", endpoint="get_all")
def get_all_images() -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_images: list = k8s.list_visa_cloud_images()
    return Response(images_to_json(k8s_images),
                    status=HTTPStatus.OK,
                    mimetype="application/json")


@bp.get("/images/<id>", endpoint="get_by_name")
def get_image_by_name(id: str) -> Response:
    k8s = current_app.extensions["kubernetes"]
    k8s_image: list = k8s.get_visa_cloud_image(id)
    return Response(images_to_json(k8s_image),
                    status=HTTPStatus.OK,
                    mimetype="application/json")
