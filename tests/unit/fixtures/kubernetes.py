from types import SimpleNamespace

import pytest
from flask import Flask

from app.utils.exceptions import KubernetesNotFoundError
from app.utils.kubernetes import VISA_K8S_CRD_LIST
from app.extensions.kubernetes import KubernetesExtension


@pytest.fixture(scope="session")
def dummy_kubernetes_extension(flavours_list, images_list, security_groups_list, devices_list) -> object:
    patcher = pytest.MonkeyPatch()

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

        @classmethod
        def list_visa_cloud_devices(cls) -> list:
            return devices_list

        @classmethod
        def get_filtered_visa_cloud_device(cls, device_type: str, identifier: str) -> list:
            for i in devices_list:
                if i.get("spec").get("type") == device_type and i.get("spec").get("identifier") == identifier:
                    return i
            raise KubernetesNotFoundError("", "")

    try:
        for name, method in DummyKubernetesExtension.__dict__.items():
            if name.startswith("_"):
                continue

            if isinstance(method, classmethod):
                method = getattr(DummyKubernetesExtension, name)
            elif not callable(method):
                continue

            patcher.setattr(KubernetesExtension, name, method)

        yield DummyKubernetesExtension
    finally:
        patcher.undo()
