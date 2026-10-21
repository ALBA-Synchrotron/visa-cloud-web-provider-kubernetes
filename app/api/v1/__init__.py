from flask import Blueprint

from auth import authenticate_api_key


def register_v1(app) -> None:
    from . import flavour

    v1: Blueprint = Blueprint("v1", __name__)
    v1.before_request(authenticate_api_key)

    for module in (flavour,):
        v1.register_blueprint(module.bp, url_prefix=f"/api/v1")

    app.register_blueprint(v1)
