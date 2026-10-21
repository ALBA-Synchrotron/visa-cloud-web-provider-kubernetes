import os


class BaseConfig:
    AUTH_API_KEY: str = os.environ.get("AUTH_API_KEY", "rubber-duck")
    AUTH_API_KEY_HEADER_NAME: str = os.environ.get("AUTH_API_KEY_HEADER_NAME", "X-Auth-Token")


class DevConfig(BaseConfig):
    DEBUG: bool = True


class TestConfig(BaseConfig):
    TESTING: bool = True


class ProdConfig(BaseConfig):
    pass


def get_config() -> BaseConfig:
    env: str = os.getenv("FLASK_ENV", "dev")
    match env:
        case "prod":
            return ProdConfig()
        case "dev":
            return DevConfig()
        case "test":
            return TestConfig()
        case _:
            return DevConfig()
