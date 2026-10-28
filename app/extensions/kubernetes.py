from flask import Flask, current_app
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.client.exceptions import NotFoundException

from app.labels.kubernetes import K8S_VISA_API_GROUP, K8S_VISA_API_VERSION, VISA_CLOUD_FLAVOURS, VISA_CLOUD_FLAVOUR, \
    VISA_CLOUD_IMAGES, VISA_CLOUD_SECURITY_GROUPS, VISA_CLOUD_INSTANCES, VISA_CLOUD_DEVICE, VISA_CLOUD_DEVICES, \
    VISA_CLOUD_INSTANCE, VISA_CLOUD_IMAGE, VISA_CLOUD_SECURITY_GROUP
from app.utils.exceptions import KubernetesError, KubernetesNotFoundError, KubernetesNotFoundInInstanceError, \
    CloudProviderResourceQuotaExceeded
from app.labels.common import ERR_FETCHING_K8S_CRDS, ERR_LISTING_PFX, ERR_STARTING_PFX, ERR_STOPPING_PFX, ERR_CREATING_PFX
from app.utils.helpers import convert_memory
from app.api.v1.serializers.flavour import flavours_to_json
from app.api.v1.serializers.instance import get_k8s_instance_body_from_payload


class KubernetesExtension:

    @classmethod
    def __common_kwargs(cls) -> dict:
        return {"group": K8S_VISA_API_GROUP, "version": K8S_VISA_API_VERSION}

    @classmethod
    def get_visa_k8s_cloud_api_resources(cls, app: Flask | None = None) -> list:
        try:
            return client.CustomObjectsApi().get_api_resources(**cls.__common_kwargs()).resources
        except ApiException as e:
            if app:
                app.logger.error(f"{ERR_FETCHING_K8S_CRDS}: {e}")
        return []

    @classmethod
    def __list_ns_cluster_custom_object(cls, obj_type_name_plural: str) -> list:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        try:
            return client.CustomObjectsApi().list_namespaced_custom_object(**cls.__common_kwargs(),
                                                                           namespace=namespace,
                                                                           plural=obj_type_name_plural).get("items")
        except (ApiException, KeyError) as e:
            raise e

    @classmethod
    def __get_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_name: str) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        try:
            return client.CustomObjectsApi().get_namespaced_custom_object(**cls.__common_kwargs(),
                                                                          namespace=namespace,
                                                                          plural=obj_type_name_plural,
                                                                          name=obj_name)
        except NotFoundException as e:
            raise e
        except (ApiException, KeyError) as e:
            raise e

    @classmethod
    def list_visa_cloud_flavours(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_FLAVOURS)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_FLAVOURS}: {e}")

    @classmethod
    def get_visa_cloud_flavour(cls, flavour_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_FLAVOURS, flavour_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=flavour_name, obj_type_name=VISA_CLOUD_FLAVOUR)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_FLAVOURS}: {e}")

    @classmethod
    def list_visa_cloud_images(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_IMAGES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_IMAGES}: {e}")

    @classmethod
    def get_visa_cloud_image(cls, image_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_IMAGES, image_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=image_name, obj_type_name=VISA_CLOUD_IMAGE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_IMAGES}: {e}")

    @classmethod
    def list_visa_cloud_security_groups(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_SECURITY_GROUPS)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_SECURITY_GROUPS}: {e}")

    @classmethod
    def get_visa_cloud_security_group(cls, sec_group_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_SECURITY_GROUPS, sec_group_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=sec_group_name, obj_type_name=VISA_CLOUD_SECURITY_GROUP)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_SECURITY_GROUPS}: {e}")

    @classmethod
    def list_visa_cloud_instances(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_INSTANCES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_INSTANCES}: {e}")

    @classmethod
    def get_visa_cloud_instance(cls, instance_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_INSTANCES, instance_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_INSTANCES}: {e}")

    @classmethod
    def __patch_visa__cloud_instance(cls, visa_cloud_instance: object) -> None:
        metadata: dict = visa_cloud_instance.get("metadata")
        instance_name: str = metadata.get("name")
        try:
            _ = client.CustomObjectsApi().patch_namespaced_custom_object(
                **cls.__common_kwargs(),
                namespace=metadata.get("namespace"),
                plural=VISA_CLOUD_INSTANCES,
                name=instance_name,
                body=visa_cloud_instance
            )
        except NotFoundException as e:
            raise e
        except (ApiException, KeyError) as e:
            raise e

    @classmethod
    def start_visa_cloud_instance(cls, instance_name: str) -> None:
        instance: object = cls.get_visa_cloud_instance(instance_name)
        try:
            instance["spec"]["desiredState"] = "ACTIVE"
            cls.__patch_visa__cloud_instance(instance)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def stop_visa_cloud_instance(cls, instance_name: str) -> None:
        instance: object = cls.get_visa_cloud_instance(instance_name)
        try:
            instance["spec"]["desiredState"] = "STOPPED"
            cls.__patch_visa__cloud_instance(instance)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STOPPING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def restart_visa_cloud_instance(cls, instance_name: str) -> None:
        instance: object = cls.get_visa_cloud_instance(instance_name)
        try:
            if instance.get("status").get("state") == "ACTIVE":
                obs_reboot_generation: int = instance.get("status").get("observedRebootGeneration", 0)
                instance["spec"]["rebootGeneration"] = obs_reboot_generation + 1
                cls.__patch_visa__cloud_instance(instance)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STOPPING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def list_visa_cloud_devices(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_DEVICES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_DEVICES}: {e}")

    @classmethod
    def get_filtered_visa_cloud_device(cls, type: str, identifier: str) -> object:
        all_devices: list = []
        try:
            all_devices = cls.__list_ns_cluster_custom_object(VISA_CLOUD_DEVICES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_DEVICES}: {e}")

        try:
            return next(
                d for d in all_devices
                if (d.get("spec") or {}).get("identifier") == identifier
                and (d.get("spec") or {}).get("type") == type
            )
        except StopIteration:
            raise KubernetesNotFoundError(obj_name=identifier, obj_type_name=VISA_CLOUD_DEVICE)

    @classmethod
    def add_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
        _: object = cls.get_visa_cloud_security_group(security_group_name)
        instance: object = cls.get_visa_cloud_instance(instance_name)
        try:
            new_sec_group: dict = {"name": security_group_name}
            if new_sec_group not in instance["spec"]["securityGroups"]:
                instance["spec"]["securityGroups"].append(new_sec_group)
                cls.__patch_visa__cloud_instance(instance)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def remove_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
        sec_group: object = cls.get_visa_cloud_security_group(security_group_name)
        instance: object = cls.get_visa_cloud_instance(instance_name)
        try:
            group_d: dict = {"name": sec_group.get("metadata").get("name")}
            if group_d in instance["spec"]["securityGroups"]:
                _ = instance["spec"]["securityGroups"].remove(group_d)
                cls.__patch_visa__cloud_instance(instance)
            else:
                raise KubernetesNotFoundInInstanceError(obj_name=security_group_name,
                                                        obj_type_name=VISA_CLOUD_SECURITY_GROUP,
                                                        obj_recipient_name=instance_name,
                                                        obj_type_recipient_name=VISA_CLOUD_INSTANCE)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def __delete_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_name: str) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        try:
            return client.CustomObjectsApi().delete_namespaced_custom_object(**cls.__common_kwargs(),
                                                                             namespace=namespace,
                                                                             plural=obj_type_name_plural,
                                                                             name=obj_name)
        except NotFoundException as e:
            raise e
        except ApiException as e:
            raise e

    @classmethod
    def delete_visa_cloud_instance(cls, instance_name: str) -> None:
        _: object = cls.get_visa_cloud_instance(instance_name)
        try:
            _ = cls.__delete_ns_cluster_custom_object(VISA_CLOUD_INSTANCES, instance_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except ApiException as e:
            raise KubernetesError(f"{ERR_STARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def __create_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_body: dict) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        try:
            return client.CustomObjectsApi().create_namespaced_custom_object(**cls.__common_kwargs(),
                                                                             namespace=namespace,
                                                                             plural=obj_type_name_plural,
                                                                             body=obj_body)
        except ApiException as e:
            raise e

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
        instance: object

        try:
            instance: object = cls.__create_ns_cluster_custom_object(VISA_CLOUD_INSTANCES, k8s_body)
        except ApiException as e:
            raise KubernetesError(f"{ERR_CREATING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

        return instance

    @classmethod
    def get_total_visa_cloud_instances_metrics(cls) -> dict:
        k8s_instances: list = cls.list_visa_cloud_instances()

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
                "max_ram": max_allocated_ram, "max_cpus": max_allocated_cpus, "max_instances": max_allocated_instances}

    @classmethod
    def __can_accommodate_new_cloud_instance(cls, flavour_name: str) -> bool:
        flavour: object = cls.get_visa_cloud_flavour(flavour_name)
        current_metrics: dict = cls.get_total_visa_cloud_instances_metrics()

        flavour_spec_limits: dict = flavour.get("spec").get("limits")
        req_cpus: float = max(int(convert_memory(flavour_spec_limits.get("cpu"))), 1) + current_metrics["in_use_cpus"]
        req_ram: float = max(int(convert_memory(flavour_spec_limits.get("memory"))), 1) + current_metrics["in_use_ram"]
        req_inst: int = current_metrics["instances_count"] + 1

        return req_cpus <= current_metrics["max_cpus"] and req_ram <= current_metrics["max_ram"] and req_inst <= \
            current_metrics["max_instances"]
