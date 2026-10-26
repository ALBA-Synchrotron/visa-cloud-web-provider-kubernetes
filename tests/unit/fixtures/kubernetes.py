from types import SimpleNamespace

from flask import Flask

from tests.unit.fixtures.flavour import DUMMY_FLAVOURS
from tests.unit.fixtures.image import DUMMY_IMAGES
from tests.unit.fixtures.security_group import DUMMY_SECURITY_GROUPS
from app.utils.exceptions import KubernetesNotFoundError
from app.utils.kubernetes import VISA_K8S_CRD_LIST


class DummyKubernetesExtension:

    @classmethod
    def get_visa_k8s_cloud_api_resources(_, __: Flask | None = None) -> list:
        return [SimpleNamespace(name=i) for i in VISA_K8S_CRD_LIST]

    @classmethod
    def list_visa_cloud_flavours(_) -> list:
        return DUMMY_FLAVOURS

    @classmethod
    def get_visa_cloud_flavour(cls, flavour_name: str) -> list:
        for i in DUMMY_FLAVOURS:
            if i.get("metadata").get("name") == flavour_name:
                return i
        raise KubernetesNotFoundError("", "")

    @classmethod
    def list_visa_cloud_images(cls) -> list:
        return DUMMY_IMAGES

    @classmethod
    def get_visa_cloud_image(cls, image_name: str) -> object:
        for i in DUMMY_IMAGES:
            if i.get("metadata").get("name") == image_name:
                return i
        raise KubernetesNotFoundError("", "")

    @classmethod
    def list_visa_cloud_security_groups(cls) -> list:
        return DUMMY_SECURITY_GROUPS
