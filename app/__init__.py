import os
from http import HTTPStatus

from flask import Flask, jsonify
from flask.typing import ResponseReturnValue

import config
from labels.common import ALL_COOLIO


def create_app(config_object="app.config.ProdConfig") -> Flask:
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    @app.get("/healthz", endpoint="healthz")
    def healthz() -> ResponseReturnValue:
        return jsonify({"status": ALL_COOLIO}), HTTPStatus.OK

    return app


app: Flask = create_app(config.get_config())
