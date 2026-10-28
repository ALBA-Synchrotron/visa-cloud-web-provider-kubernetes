from http import HTTPStatus

from flask import Blueprint, current_app, Response

from v1.serializers.metrics import metrics_to_json

bp: Blueprint = Blueprint("metrics", __name__)


@bp.get("/metrics", endpoint="get_all")
def get_all_cloud_provider_metrics() -> Response:
    k8s = current_app.extensions["kubernetes"]

    k8s_metrics: dict = {
        **k8s.get_total_visa_cloud_instances_metrics()
    }
    return Response(metrics_to_json(k8s_metrics),
                    status=HTTPStatus.OK,
                    mimetype="application/json")
