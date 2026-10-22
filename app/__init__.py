from http import HTTPStatus
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue

from error_handlers import register_error_handlers
from labels.common import ALL_COOLIO, INIT_APP

import config as app_config
from logging_config import configure_logging
from utils.kubernetes import initialize_kubernetes
from v1 import register_v1


def create_app(config_object: app_config.BaseConfig) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    configure_logging(app)
    app.logger.info(INIT_APP)

    register_v1(app)
    register_error_handlers(app)

    initialize_kubernetes(app)

    @app.get("/healthz", endpoint="healthz")
    def healthz() -> ResponseReturnValue:
        return jsonify({"status": ALL_COOLIO}), HTTPStatus.OK

    return app
