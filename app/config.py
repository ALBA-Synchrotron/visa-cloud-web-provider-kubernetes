import os


class BaseConfig:
    AUTH_API_KEY: str = os.environ.get("AUTH_API_KEY", "rubber-duck")
    AUTH_API_KEY_HEADER_NAME: str = os.environ.get("AUTH_API_KEY_HEADER_NAME", "X-Auth-Token")
    K8S_CONFIG_SOURCE: str = os.environ.get("K8S_CONFIG_SOURCE", "kubeconfig")
    K8S_CONFIG_FILE_PATH: str = os.environ.get("K8S_CONFIG_FILE_PATH", "~/.kube/config")
    K8S_NAMESPACE: str = os.environ.get("K8S_NAMESPACE", "visa-pods-test")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "DEBUG")
    TEST_MODE: str = ""
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "5000"))
    AUTO_START_INSTANCES_ON_CREATION: bool = bool(os.getenv(
        "AUTO_START_INSTANCES_ON_CREATION", True
    ))
    MAX_RAM_ALLOCATED: float = float(os.environ.get("MAX_RAM_ALLOCATED", 51200))
    MAX_INSTANCES_ALLOCATED: int = int(os.environ.get("MAX_INSTANCES_ALLOCATED", 20))
    MAX_CORES_ALLOCATED: float = float(os.environ.get("MAX_CORES_ALLOCATED", 15))
    IGNORE_SEC_GROUP_NOT_FOUND_ERRORS: bool = bool(os.environ.get("IGNORE_SEC_GROUP_NOT_FOUND_ERRORS", True))
    ENFORCE_MAX_QUOTAS: bool = bool(os.environ.get("ENFORCE_MAX_QUOTAS", True))


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
