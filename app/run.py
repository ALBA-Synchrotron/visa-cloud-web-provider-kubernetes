from flask import Flask

import config as app_config
from app import create_app

app: Flask = create_app(app_config.get_config())

if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"]
    )
