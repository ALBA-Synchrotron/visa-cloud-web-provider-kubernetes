import time

from flask import Flask
from kubernetes import config as k8s_config

from app.extensions.kubernetes import KubernetesExtension
from app.labels.common import INIT_K8S, ERR_K8S_CONF_LOAD, ERR_K8S_CRD_NOT_FOUND
from app.utils.exceptions import APIConfigError, VISAK8sInstallError

VISA_K8S_CRD_LIST: list = ['visacloudsecuritygroups', 'visacloudimages', 'visacloudinstances',
                           'visacloudinstances/status',
                           'visacloudflavours', 'visaclouddevices', 'visacloudsidecarconfigs']


def load_kubernetes_config(app: Flask) -> None:
    with app.app_context():
        app.logger.info(INIT_K8S)
        k8s_config_src: str = app.config["K8S_CONFIG_SOURCE"]
        try:
            match k8s_config_src:
                case "kubeconfig":
                    k8s_config.load_kube_config(config_file=app.config["K8S_CONFIG_FILE_PATH"])
                case "serviceaccount":
                    k8s_config.load_incluster_config()
        except k8s_config.ConfigException as e:
            error_msg: str = f"{ERR_K8S_CONF_LOAD} (source={k8s_config_src}): {e}"
            app.logger.error(error_msg)
            raise APIConfigError(error_msg)


def validate_visa_kubernetes_crd_are_available(app) -> None:
    with app.app_context():
        k8s = app.extensions["kubernetes"]

        visa_kinds = k8s.get_visa_k8s_cloud_api_resources()
        try:
            assert sorted([i.name for i in visa_kinds]) == sorted(VISA_K8S_CRD_LIST)
        except AssertionError:
            error_msg: str = ERR_K8S_CRD_NOT_FOUND
            app.logger.error(error_msg)
            raise VISAK8sInstallError(error_msg)


def initialize_kubernetes(app: Flask) -> None:
    with app.app_context():
        app.extensions["kubernetes"] = KubernetesExtension()

        if app.config["TEST_MODE"] != "unit":
            load_kubernetes_config(app)

        validate_visa_kubernetes_crd_are_available(app)


def wait_until_empty(api: object, group: str, version: str, namespace: str, plural: str, timeout: int = 45) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        result = api.list_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
        )

        if not result.get("items"):
            return

        time.sleep(0.5)

    raise TimeoutError(f"{plural} were not deleted within {timeout}s")
