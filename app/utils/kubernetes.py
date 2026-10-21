from flask import Flask
from kubernetes import config as k8s_config

from labels.common import INIT_K8S, ERR_K8S_CONF_LOAD, ERR_K8S_CRD_NOT_FOUND
from utils.exceptions import APIConfigError, VISAK8sInstallError
from extensions import KubernetesExtension

VISA_K8S_CRD_LIST: list = ['visacloudsecuritygroups', 'visacloudimages', 'visainstances', 'visainstances/status',
                           'visacloudflavours', 'visaclouddevices', 'visasidecarconfigs']


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

    app.extensions["kubernetes"] = KubernetesExtension()


def validate_visa_kubernetes_crd_are_available(app) -> None:
    with app.app_context():
        visa_k8s_api_group: str = app.config["K8S_VISA_API_GROUP"]
        visa_kis_api_version: str = app.config["K8S_VISA_API_VERSION"]

        k8s = app.extensions["kubernetes"]

        visa_kinds = k8s.get_api_resources(group=visa_k8s_api_group, version=visa_kis_api_version)
        try:
            assert sorted([i.name for i in visa_kinds]) == sorted(VISA_K8S_CRD_LIST)
        except AssertionError:
            error_msg: str = ERR_K8S_CRD_NOT_FOUND
            app.logger.error(error_msg)
            raise VISAK8sInstallError(error_msg)


def initialize_kubernetes(app: Flask) -> None:
    load_kubernetes_config(app)
    validate_visa_kubernetes_crd_are_available(app)
