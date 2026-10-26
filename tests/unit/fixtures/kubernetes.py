from types import SimpleNamespace

import pytest
from flask import Flask

from app.utils.exceptions import KubernetesNotFoundError
from app.utils.kubernetes import VISA_K8S_CRD_LIST
from app.extensions.kubernetes import KubernetesExtension


@pytest.fixture(scope="session")
def dummy_kubernetes_extension(monkeypatch, flavours_list, images_list, security_groups_list) -> object:
    class DummyKubernetesExtension:
        @classmethod
        def get_visa_k8s_cloud_api_resources(cls, __: Flask | None = None) -> list:
            return [SimpleNamespace(name=i) for i in VISA_K8S_CRD_LIST]

        @classmethod
        def list_visa_cloud_flavours(cls):
            return flavours_list

        @classmethod
        def get_visa_cloud_flavour(cls, flavour_name: str) -> list:
            for i in flavours_list:
                if i.get("metadata").get("name") == flavour_name:
                    return i
            raise KubernetesNotFoundError("", "")

        @classmethod
        def list_visa_cloud_images(cls) -> list:
            return images_list

        @classmethod
        def get_visa_cloud_image(cls, image_name: str) -> object:
            for i in images_list:
                if i.get("metadata").get("name") == image_name:
                    return i
            raise KubernetesNotFoundError("", "")

        @classmethod
        def list_visa_cloud_security_groups(cls) -> list:
            return security_groups_list


    for name, method in DummyKubernetesExtension.__dict__.items():
        if name.startswith("_"):
            continue

        if isinstance(method, classmethod):
            method = getattr(DummyKubernetesExtension, name)
        elif not callable(method):
            continue

        monkeypatch.setattr(KubernetesExtension, name, method)


    return DummyKubernetesExtension



