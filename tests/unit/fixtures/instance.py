import pytest


@pytest.fixture(scope="session")
def instances_list() -> list[dict]:
    return [
        {
            "apiVersion": "cloudprovider.visa.k8s/v1",
            "kind": "VISACloudInstance",
            "metadata": {
                "annotations": {
                    "cloudprovider.visa.k8s/bootCommand": "",
                    "cloudprovider.visa.k8s/instruments": "",
                    "cloudprovider.visa.k8s/keyboardLayout": "es-es-qwerty",
                    "cloudprovider.visa.k8s/owner": "rcabezas",
                    "cloudprovider.visa.k8s/pamPublicKey": "-----BEGIN PUBLIC KEY-----\n42\n-----END PUBLIC KEY-----\n",
                    "cloudprovider.visa.k8s/proposals": "",
                    "cloudprovider.visa.k8s/screenHeight": "1080",
                    "cloudprovider.visa.k8s/screenWidth": "1920"
                },
                "creationTimestamp": "2026-10-28T10:03:10Z",
                "finalizers": [
                    "cloudprovider.visa.k8s/finalizer"
                ],
                "generation": 2,
                "labels": {
                    "cloudprovider.visa.k8s/id": "895",
                    "cloudprovider.visa.k8s/uid": "XHmd8T0y"
                },
                "name": "rcq-895",
                "namespace": "visa-k8s-test-e2e",
                "resourceVersion": "172047",
                "uid": "2acb9c23-c2e1-4db5-a827-65b08bb24186"
            },
            "spec": {
                "associatedProposals": [
                    ""
                ],
                "desiredState": "ACTIVE",
                "flavour": {
                    "name": "test-flavour-1"
                },
                "image": {
                    "name": "test-image-1"
                },
                "securityGroups": [
                    {
                        "name": "instance-sudoers"
                    }
                ]
            },
            "status": {
                "address": "10.244.0.16",
                "conditions": [
                    {
                        "lastTransitionTime": "2026-10-28T10:04:31Z",
                        "message": "Instance is ready",
                        "reason": "Ready",
                        "status": "True",
                        "type": "Ready"
                    },
                    {
                        "lastTransitionTime": "2026-10-28T10:03:10Z",
                        "message": "Backing pod has been created",
                        "reason": "PodCreated",
                        "status": "True",
                        "type": "Provisioned"
                    }
                ],
                "error": {},
                "state": "ACTIVE"
            }
        },
        {
            "apiVersion": "cloudprovider.visa.k8s/v1",
            "kind": "VISACloudInstance",
            "metadata": {
                "annotations": {
                    "cloudprovider.visa.k8s/bootCommand": "",
                    "cloudprovider.visa.k8s/instruments": "BL13 - XALOC,BL06 - XAIRA,BL31 - FAXTOR,BL11 - NCD-SWEET",
                    "cloudprovider.visa.k8s/keyboardLayout": "es-es-qwerty",
                    "cloudprovider.visa.k8s/owner": "rcabezas",
                    "cloudprovider.visa.k8s/pamPublicKey": "-----BEGIN PUBLIC KEY-----\n42\n-----END PUBLIC KEY-----\n",
                    "cloudprovider.visa.k8s/proposals": "2023097843,2025003333,20250370148,20250370148,2024098712,20250370148,2025003333",
                    "cloudprovider.visa.k8s/screenHeight": "1080",
                    "cloudprovider.visa.k8s/screenWidth": "1920"
                },
                "creationTimestamp": "2026-10-28T10:11:44Z",
                "finalizers": [
                    "cloudprovider.visa.k8s/finalizer"
                ],
                "generation": 1,
                "labels": {
                    "cloudprovider.visa.k8s/id": "897",
                    "cloudprovider.visa.k8s/uid": "etMe0MjE"
                },
                "name": "rcq-897",
                "namespace": "visa-k8s-test-e2e",
                "resourceVersion": "172871",
                "uid": "bf356b8b-edce-4350-b8d0-71aee1a1dff7"
            },
            "spec": {
                "associatedProposals": [
                    "2023097843",
                    "2025003333",
                    "20250370148",
                    "20250370148",
                    "2024098712",
                    "20250370148",
                    "2025003333"
                ],
                "desiredState": "ACTIVE",
                "flavour": {
                    "name": "test-flavour-1"
                },
                "image": {
                    "name": "test-image-1"
                },
                "securityGroups": [
                    {
                        "name": "u2023097843"
                    },
                    {
                        "name": "u2025003333"
                    },
                    {
                        "name": "u2024098712"
                    }
                ]
            }
        }
    ]

@pytest.fixture
def test_instance(dummy_kubernetes_extension) -> dict:
    return dummy_kubernetes_extension.instances_list[0]
