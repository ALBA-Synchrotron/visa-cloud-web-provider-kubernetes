from flask import Flask

from app import config as app_config
from app import create_app

app: Flask = create_app(app_config.get_config())