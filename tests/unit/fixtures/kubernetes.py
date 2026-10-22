from types import SimpleNamespace

from flask import Flask

from fixtures.flavour import DUMMY_FLAVOURS
from utils.exceptions import KubernetesNotFoundError
from utils.kubernetes import VISA_K8S_CRD_LIST


class DummyKubernetesExtension:

    @classmethod
    def get_visa_k8s_cloud_api_resources(_, __: Flask | None = None) -> list:
        return [SimpleNamespace(name=i) for i in VISA_K8S_CRD_LIST]

    @classmethod
    def list_visa_cloud_flavours(_) -> list:
        return DUMMY_FLAVOURS

    @classmethod
    def get_visa_cloud_flavour(cls, name: str) -> list:
        for i in DUMMY_FLAVOURS:
            if i.get("metadata").get("name") == name:
                return i
        raise KubernetesNotFoundError("", "")
