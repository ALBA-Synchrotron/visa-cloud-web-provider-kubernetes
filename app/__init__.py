from http import HTTPStatus
from flask import Flask, jsonify
from flask.typing import ResponseReturnValue
from labels.common import ALL_COOLIO, INIT_APP

import config as app_config
from logging_config import configure_logging
from utils.kubernetes import initialize_kubernetes


def create_app(config_object: app_config.BaseConfig) -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    configure_logging(app)

    app.logger.info(INIT_APP)

    initialize_kubernetes(app)

    @app.get("/healthz", endpoint="healthz")
    def healthz() -> ResponseReturnValue:
        return jsonify({"status": ALL_COOLIO}), HTTPStatus.OK

    return app


app: Flask = create_app(app_config.get_config())
