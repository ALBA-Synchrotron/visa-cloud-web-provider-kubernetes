import os


class BaseConfig:
    AUTH_API_KEY: str = os.environ.get("AUTH_API_KEY", "rubber-duck")
    AUTH_API_KEY_HEADER_NAME: str = os.environ.get("AUTH_API_KEY_HEADER_NAME", "X-Auth-Token")
    K8S_CONFIG_SOURCE: str = os.environ.get("K8S_CONFIG_SOURCE", "kubeconfig")
    K8S_CONFIG_FILE_PATH: str = os.environ.get("K8S_CONFIG_FILE_PATH", "/kubeconfig")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "DEBUG")
    K8S_VISA_API_GROUP: str = os.environ.get("K8S_VISA_API_GROUP", "cloudprovider.visa.k8s")
    K8S_VISA_API_VERSION: str = os.environ.get("K8S_VISA_API_VERSION", "v1")


class DevConfig(BaseConfig):
    DEBUG: bool = True


class TestConfig(BaseConfig):
    TESTING: bool = True


class ProdConfig(BaseConfig):
    K8S_CONFIG_SOURCE: str = os.environ.get("K8S_CONFIG_SOURCE", "serviceaccount")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

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
