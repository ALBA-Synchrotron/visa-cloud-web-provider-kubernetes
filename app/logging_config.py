import logging
import sys

from flask import Flask


def configure_logging(app: Flask) -> None:
    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt=(
                "%(asctime)s | %(levelname)s | "
                "%(name)s | %(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    app.logger.propagate = False

    werkzeug_logger: logging.Logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(app.logger.level)
