import time

from flask import Flask, current_app
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.client.exceptions import NotFoundException

from app.labels.kubernetes import K8S_VISA_API_GROUP, K8S_VISA_API_VERSION, VISA_CLOUD_FLAVOURS, VISA_CLOUD_FLAVOUR, \
    VISA_CLOUD_IMAGES, VISA_CLOUD_SECURITY_GROUPS, VISA_CLOUD_INSTANCES, VISA_CLOUD_DEVICE, VISA_CLOUD_DEVICES, \
    VISA_CLOUD_INSTANCE, VISA_CLOUD_IMAGE, VISA_CLOUD_SECURITY_GROUP
from app.utils.exceptions import KubernetesError, KubernetesNotFoundError, KubernetesNotFoundInInstanceError, \
    CloudProviderResourceQuotaExceeded
from app.labels.common import ERR_FETCHING_K8S_CRDS, ERR_LISTING_PFX, ERR_STARTING_PFX, ERR_STOPPING_PFX, \
    ERR_CREATING_PFX, ERR_RESTARTING_PFX, ERR_UPDATING_PFX, ERR_DELETING_PFX
from app.utils.helpers import convert_memory, to_cores
from app.api.v1.serializers.flavour import flavours_to_json
from app.api.v1.serializers.instance import get_k8s_instance_body_from_payload

PATCH_CONFLICT_RETRIES: int = 5
PATCH_CONFLICT_BACKOFF_SECONDS: float = 0.1


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
        return client.CustomObjectsApi().list_namespaced_custom_object(**cls.__common_kwargs(),
                                                                       namespace=namespace,
                                                                       plural=obj_type_name_plural).get("items")

    @classmethod
    def __get_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_name: str) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        return client.CustomObjectsApi().get_namespaced_custom_object(**cls.__common_kwargs(),
                                                                      namespace=namespace,
                                                                      plural=obj_type_name_plural,
                                                                      name=obj_name)

    @classmethod
    def __delete_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_name: str) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        return client.CustomObjectsApi().delete_namespaced_custom_object(**cls.__common_kwargs(),
                                                                         namespace=namespace,
                                                                         plural=obj_type_name_plural,
                                                                         name=obj_name)

    @classmethod
    def __create_ns_cluster_custom_object(cls, obj_type_name_plural: str, obj_body: dict) -> object:
        namespace: str = current_app.config["K8S_NAMESPACE"]
        return client.CustomObjectsApi().create_namespaced_custom_object(**cls.__common_kwargs(),
                                                                         namespace=namespace,
                                                                         plural=obj_type_name_plural,
                                                                         body=obj_body)

    @classmethod
    def __update_visa_cloud_instance_spec(cls, instance_name: str, build_spec_patch,
                                          retries: int = PATCH_CONFLICT_RETRIES) -> None:
        for attempt in range(retries):
            instance: dict = cls.get_visa_cloud_instance(instance_name)
            spec_patch: dict | None = build_spec_patch(instance)
            if not spec_patch:
                return

            metadata: dict = instance["metadata"]
            body: dict = {
                "metadata": {"resourceVersion": metadata["resourceVersion"]},
                "spec": spec_patch,
            }
            try:
                client.CustomObjectsApi().patch_namespaced_custom_object(
                    **cls.__common_kwargs(),
                    namespace=metadata["namespace"],
                    plural=VISA_CLOUD_INSTANCES,
                    name=metadata["name"],
                    body=body,
                )
                return
            except ApiException as e:
                if e.status == 409 and attempt < retries - 1:
                    time.sleep(PATCH_CONFLICT_BACKOFF_SECONDS * (attempt + 1))
                    continue
                raise

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
    def start_visa_cloud_instance(cls, instance_name: str) -> None:
        def build(instance: dict) -> dict | None:
            if instance["spec"].get("desiredState") == "ACTIVE":
                return None
            return {"desiredState": "ACTIVE"}

        try:
            cls.__update_visa_cloud_instance_spec(instance_name, build)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def stop_visa_cloud_instance(cls, instance_name: str) -> None:
        def build(instance: dict) -> dict | None:
            if instance["spec"].get("desiredState") == "STOPPED":
                return None
            return {"desiredState": "STOPPED"}

        try:
            cls.__update_visa_cloud_instance_spec(instance_name, build)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_STOPPING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def restart_visa_cloud_instance(cls, instance_name: str) -> None:
        def build(instance: dict) -> dict | None:
            status: dict = instance.get("status") or {}
            if status.get("state") != "ACTIVE":
                return None
            return {"rebootGeneration": status.get("observedRebootGeneration", 0) + 1}

        try:
            cls.__update_visa_cloud_instance_spec(instance_name, build)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_RESTARTING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def add_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
        cls.get_visa_cloud_security_group(security_group_name)
        new_sec_group: dict = {"name": security_group_name}

        def build(instance: dict) -> dict | None:
            sec_groups: list = list(instance["spec"].get("securityGroups") or [])
            if new_sec_group in sec_groups:
                return None
            sec_groups.append(new_sec_group)
            return {"securityGroups": sec_groups}

        try:
            cls.__update_visa_cloud_instance_spec(instance_name, build)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_UPDATING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def remove_security_group_to_instance(cls, instance_name: str, security_group_name: str) -> None:
        cls.get_visa_cloud_security_group(security_group_name) 
        rem_sec_group: dict = {"name": security_group_name}

        def build(instance: dict) -> dict | None:
            sec_groups: list = list(instance["spec"].get("securityGroups") or [])
            if rem_sec_group not in sec_groups:
                raise KubernetesNotFoundInInstanceError(obj_name=security_group_name,
                                                        obj_type_name=VISA_CLOUD_SECURITY_GROUP,
                                                        obj_recipient_name=instance_name,
                                                        obj_type_recipient_name=VISA_CLOUD_INSTANCE)
            sec_groups.remove(rem_sec_group)
            return {"securityGroups": sec_groups}

        try:
            cls.__update_visa_cloud_instance_spec(instance_name, build)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_UPDATING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def delete_visa_cloud_instance(cls, instance_name: str) -> None:
        try:
            cls.__delete_ns_cluster_custom_object(VISA_CLOUD_INSTANCES, instance_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=instance_name, obj_type_name=VISA_CLOUD_INSTANCE)
        except ApiException as e:
            raise KubernetesError(f"{ERR_DELETING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def create_visa_cloud_instance(cls, instance_body: dict) -> object:
        image_name: str = instance_body.get("imageId")
        flavour_name: str = instance_body.get("flavourId")
        sec_groups: list = instance_body.get("securityGroups") or []

        cls.get_visa_cloud_image(image_name)
        flavour: object = cls.get_visa_cloud_flavour(flavour_name)

        if not current_app.config["IGNORE_SEC_GROUP_NOT_FOUND_ERRORS"]:
            for group in sec_groups:
                cls.get_visa_cloud_security_group(group)

        if not cls.__can_accommodate_new_cloud_instance(flavour):
            raise CloudProviderResourceQuotaExceeded()

        k8s_body: dict = get_k8s_instance_body_from_payload(instance_body)

        try:
            return cls.__create_ns_cluster_custom_object(VISA_CLOUD_INSTANCES, k8s_body)
        except ApiException as e:
            raise KubernetesError(f"{ERR_CREATING_PFX} {VISA_CLOUD_INSTANCE}: {e}")

    @classmethod
    def list_visa_cloud_devices(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_DEVICES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"{ERR_LISTING_PFX} {VISA_CLOUD_DEVICES}: {e}")

    @classmethod
    def get_filtered_visa_cloud_device(cls, type: str, identifier: str) -> object:
        all_devices: list = cls.list_visa_cloud_devices()

        try:
            return next(
                d for d in all_devices
                if (d.get("spec") or {}).get("identifier") == identifier
                and (d.get("spec") or {}).get("type") == type
            )
        except StopIteration:
            raise KubernetesNotFoundError(obj_name=identifier, obj_type_name=VISA_CLOUD_DEVICE)

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
            flavour_name: str | None = ((instance.get("spec") or {}).get("flavour") or {}).get("name")
            flavour: dict | None = flavours.get(flavour_name)
            if flavour is None:
                current_app.logger.warning(
                    f"Instance {(instance.get('metadata') or {}).get('name')} references unknown "
                    f"flavour '{flavour_name}'; skipping it in resource metrics")
                continue
            in_use_cpus += flavour["cpus"]
            in_use_ram += flavour["ram"]

        return {"in_use_cpus": in_use_cpus, "in_use_ram": in_use_ram, "instances_count": len(k8s_instances),
                "max_ram": max_allocated_ram, "max_cpus": max_allocated_cpus, "max_instances": max_allocated_instances}

    @classmethod
    def __can_accommodate_new_cloud_instance(cls, flavour: object) -> bool:
        current_metrics: dict = cls.get_total_visa_cloud_instances_metrics()

        flavour_spec_limits: dict = flavour.get("spec").get("limits")
        req_cpus: float = max(int(to_cores(flavour_spec_limits.get("cpu"))), 1) + current_metrics["in_use_cpus"]
        req_ram: float = max(int(convert_memory(flavour_spec_limits.get("memory"))), 1) + current_metrics["in_use_ram"]
        req_inst: int = current_metrics["instances_count"] + 1

        return (req_cpus <= current_metrics["max_cpus"]
                and req_ram <= current_metrics["max_ram"]
                and req_inst <= current_metrics["max_instances"])
