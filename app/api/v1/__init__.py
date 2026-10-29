from flask import Blueprint

from app.auth import authenticate_api_key


def register_v1(app) -> None:
    from . import flavour
    from . import hypervisor
    from . import image
    from . import instance
    from . import metrics
    from . import security_group
    from . import device

    v1: Blueprint = Blueprint("v1", __name__)
    v1.before_request(authenticate_api_key)

    for module in (flavour, hypervisor, image, instance, security_group, metrics, device):
        v1.register_blueprint(module.bp, url_prefix=f"/v1/api")

    app.register_blueprint(v1)
