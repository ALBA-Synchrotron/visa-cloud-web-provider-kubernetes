from flask import Flask
from kubernetes import client
from kubernetes.client import ApiException


class KubernetesExtension:

    @staticmethod
    def get_api_resources(group: str, version: str, app: Flask | None = None) -> list:
        try:
            return client.CustomObjectsApi().get_api_resources(group=group, version=version).resources
        except ApiException as e:
            if app:
                app.logger.error(f"Error getting Kubernetes VISA-k8s API resources: {e}")
        return []
