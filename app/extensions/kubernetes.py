from flask import Flask, current_app
from kubernetes import client
from kubernetes.client import ApiException
from kubernetes.client.exceptions import NotFoundException

from app.labels.kubernetes import K8S_VISA_API_GROUP, K8S_VISA_API_VERSION, VISA_CLOUD_FLAVOURS, VISA_CLOUD_FLAVOUR, \
    VISA_CLOUD_IMAGES, VISA_CLOUD_SECURITY_GROUPS, VISA_CLOUD_INSTANCES
from app.utils.exceptions import KubernetesError, KubernetesNotFoundError


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
                app.logger.error(f"Error getting Kubernetes VISA-k8s API resources: {e}")
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
            raise KubernetesError(f"Error listing {VISA_CLOUD_FLAVOURS}: {e}")

    @classmethod
    def get_visa_cloud_flavour(cls, flavour_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_FLAVOURS, flavour_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=flavour_name, obj_type_name=VISA_CLOUD_FLAVOUR)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"Error listing {VISA_CLOUD_FLAVOURS}: {e}")

    @classmethod
    def list_visa_cloud_images(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_IMAGES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"Error listing {VISA_CLOUD_IMAGES}: {e}")

    @classmethod
    def get_visa_cloud_image(cls, image_name: str) -> object:
        try:
            return cls.__get_ns_cluster_custom_object(VISA_CLOUD_IMAGES, image_name)
        except NotFoundException:
            raise KubernetesNotFoundError(obj_name=image_name, obj_type_name=VISA_CLOUD_IMAGES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"Error listing {VISA_CLOUD_IMAGES}: {e}")

    @classmethod
    def list_visa_cloud_security_groups(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_SECURITY_GROUPS)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"Error listing {VISA_CLOUD_SECURITY_GROUPS}: {e}")

    @classmethod
    def list_visa_cloud_instances(cls) -> list:
        try:
            return cls.__list_ns_cluster_custom_object(VISA_CLOUD_INSTANCES)
        except (ApiException, KeyError) as e:
            raise KubernetesError(f"Error listing {VISA_CLOUD_INSTANCES}: {e}")
