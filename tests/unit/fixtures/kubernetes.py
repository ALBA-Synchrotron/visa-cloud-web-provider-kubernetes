from types import SimpleNamespace

import pytest
from flask import Flask, current_app

from app.utils.exceptions import KubernetesNotFoundError, CloudProviderResourceQuotaExceeded
from app.utils.kubernetes import VISA_K8S_CRD_LIST
from app.extensions.kubernetes import KubernetesExtension
from utils.helpers import convert_memory
from v1.serializers.flavour import flavours_to_json
from v1.serializers.instance import get_k8s_instance_body_from_payload


@pytest.fixture(scope="session")
def dummy_kubernetes_extension(flavours_list, images_list, security_groups_list, devices_list) -> object:
    patcher = pytest.MonkeyPatch()

    class DummyKubernetesExtension:

        instances_list: list = []

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

        @classmethod
        def list_visa_cloud_instances(cls) -> list:
            return cls.instances_list

        @classmethod
        def get_visa_cloud_instance(cls, instance_name: str) -> object:
            for i in cls.instances_list:
                if i.get("metadata").get("name") == instance_name:
                    return i
            raise KubernetesNotFoundError("", "")

        @classmethod
        def start_visa_cloud_instance(cls, instance_name: str) -> None:
            _: object = cls.get_visa_cloud_instance(instance_name)

        @classmethod
        def stop_visa_cloud_instance(cls, instance_name: str) -> None:
            _: object = cls.get_visa_cloud_instance(instance_name)

        @classmethod
        def restart_visa_cloud_instance(cls, instance_name: str) -> None:
            _: object = cls.get_visa_cloud_instance(instance_name)

        @classmethod
        def add_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
            instance: object = cls.get_visa_cloud_instance(instance_name)
            instance.get("spec").get("securityGroups").append({"name": security_group_name})

        @classmethod
        def remove_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
            instance: object = cls.get_visa_cloud_instance(instance_name)
            instance.get("spec").get("securityGroups").remove({"name": security_group_name})

        @classmethod
        def delete_visa_cloud_instance(cls, instance_name: str) -> None:
            instance: object = cls.get_visa_cloud_instance(instance_name)
            cls.instances_list.remove(instance)

        @classmethod
        def get_visa_cloud_security_group(cls, sec_group_name: str) -> object:
            for i in security_groups_list:
                if i.get("metadata").get("name") == sec_group_name:
                    return i
            raise KubernetesNotFoundError("", "")

        @classmethod
        def get_total_visa_cloud_instances_metrics(cls) -> dict:
            k8s_instances: list = cls.instances_list

            max_allocated_ram: float = current_app.config["MAX_RAM_ALLOCATED"]
            max_allocated_instances: float = current_app.config["MAX_INSTANCES_ALLOCATED"]
            max_allocated_cpus: float = current_app.config["MAX_CORES_ALLOCATED"]

            in_use_cpus: float = 0
            in_use_ram: float = 0

            flavours: dict = {i.get("name"): {"cpus": i.get("cpus"), "ram": i.get("ram")} for i in
                              flavours_to_json(cls.list_visa_cloud_flavours(), dump=False)}

            for instance in k8s_instances:
                flavour_name: str = instance.get("spec").get("flavour").get("name")
                in_use_cpus += flavours[flavour_name]["cpus"]
                in_use_ram += flavours[flavour_name]["ram"]

            return {"in_use_cpus": in_use_cpus, "in_use_ram": in_use_ram, "instances_count": len(k8s_instances),
                    "max_ram": max_allocated_ram, "max_cpus": max_allocated_cpus,
                    "max_instances": max_allocated_instances}

        @classmethod
        def __can_accommodate_new_cloud_instance(cls, flavour_name: str) -> bool:
            flavour: object = cls.get_visa_cloud_flavour(flavour_name)
            current_metrics: dict = cls.get_total_visa_cloud_instances_metrics()

            flavour_spec_limits: dict = flavour.get("spec").get("limits")
            req_cpus: float = max(int(convert_memory(flavour_spec_limits.get("cpu"))), 1) + current_metrics[
                "in_use_cpus"]
            req_ram: float = max(int(convert_memory(flavour_spec_limits.get("memory"))), 1) + current_metrics[
                "in_use_ram"]
            req_inst: int = current_metrics["instances_count"] + 1

            return req_cpus <= current_metrics["max_cpus"] and req_ram <= current_metrics["max_ram"] and req_inst <= \
                current_metrics["max_instances"]

        @classmethod
        def create_visa_cloud_instance(cls, instance_body: dict) -> object:
            image_name: str = instance_body.get("imageId")
            flavour_name: str = instance_body.get("flavourId")
            sec_groups: list = instance_body.get("securityGroups")

            _: object = cls.get_visa_cloud_image(image_name)
            _: object = cls.get_visa_cloud_flavour(flavour_name)

            if not current_app.config["IGNORE_SEC_GROUP_NOT_FOUND_ERRORS"]:
                for group in sec_groups:
                    _: object = cls.get_visa_cloud_security_group(group)

            if not cls.__can_accommodate_new_cloud_instance(flavour_name):
                raise CloudProviderResourceQuotaExceeded()

            k8s_body: dict = get_k8s_instance_body_from_payload(instance_body)
            cls.instances_list.append(k8s_body)

            return k8s_body

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


@pytest.fixture(autouse=True)
def reset_dummy_instances(dummy_kubernetes_extension, instances_list):
    dummy_kubernetes_extension.instances_list = instances_list
