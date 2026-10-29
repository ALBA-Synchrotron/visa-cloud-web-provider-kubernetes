import pytest
from kubernetes import config, client

from app.labels.kubernetes import K8S_VISA_API_GROUP, K8S_VISA_API_VERSION, VISA_CLOUD_INSTANCES
from app.utils.kubernetes import wait_until_empty
from .yaml import load_yaml_resources


@pytest.fixture
def instances_list() -> list:
    return load_yaml_resources(kind="VISACloudInstance")


@pytest.fixture
def test_instance(instances_list) -> dict:
    return instances_list[0]


@pytest.fixture
def reset_instances(app, instances_list) -> None:
    config.load_kube_config()

    api = client.CustomObjectsApi()

    _ = api.delete_collection_namespaced_custom_object(group=K8S_VISA_API_GROUP,
                                                       version=K8S_VISA_API_VERSION,
                                                       namespace=app.config["K8S_NAMESPACE"],
                                                       plural=VISA_CLOUD_INSTANCES)

    wait_until_empty(api, group=K8S_VISA_API_GROUP,
                     version=K8S_VISA_API_VERSION,
                     namespace=app.config["K8S_NAMESPACE"],
                     plural=VISA_CLOUD_INSTANCES)

    for obj in instances_list:
        if obj:
            a = api.create_namespaced_custom_object(
                group=K8S_VISA_API_GROUP,
                version=K8S_VISA_API_VERSION,
                namespace=app.config["K8S_NAMESPACE"],
                plural=VISA_CLOUD_INSTANCES,
                body=obj,
            )
            print(a)

    return
