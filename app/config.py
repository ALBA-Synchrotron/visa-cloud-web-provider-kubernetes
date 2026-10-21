import os


class BaseConfig:
    AUTH_API_KEY: str = os.environ.get("AUTH_API_KEY", "rubber-duck")
    AUTH_API_KEY_HEADER_NAME: str = os.environ.get("AUTH_API_KEY_HEADER_NAME", "X-Auth-Token")
    K8S_CONFIG_SOURCE: str = os.environ.get("K8S_CONFIG_SOURCE", "kubeconfig")
    K8S_CONFIG_FILE_PATH: str = os.environ.get("K8S_CONFIG_FILE_PATH", "/kubeconfig")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "DEBUG")
    K8S_VISA_API_GROUP: str = os.environ.get("K8S_VISA_API_GROUP", "cloudprovider.visa.k8s")
    K8S_VISA_API_VERSION: str = os.environ.get("K8S_VISA_API_VERSION", "v1")
    TEST_MODE: str = ""
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "5000"))


class DevConfig(BaseConfig):
    DEBUG: bool = True


class TestConfig(BaseConfig):
    TESTING: bool = True


class UnitTestConfig(TestConfig):
    TEST_MODE: str = "unit"


class IntegrationTestConfig(TestConfig):
    TEST_MODE: str = "integration"


class ProdConfig(BaseConfig):
    K8S_CONFIG_SOURCE: str = os.environ.get("K8S_CONFIG_SOURCE", "serviceaccount")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")


def get_config() -> BaseConfig:
    env: str = os.getenv("FLASK_ENV", "dev")
    test_mode: str = os.environ.get("TESTING_MODE", "unit")

    match env:
        case "prod":
            return ProdConfig()
        case "dev":
            return DevConfig()
        case "test":
            match test_mode:
                case "unit":
                    return UnitTestConfig()
                case "integration":
                    return IntegrationTestConfig()
                case _:
                    return TestConfig()
        case _:
            return DevConfig()
