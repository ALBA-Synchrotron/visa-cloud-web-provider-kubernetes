from http import HTTPStatus

from flask import url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.instance"


def test_create_instance(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        r_data: list = r.get_json()
        assert r.status_code == HTTPStatus.CREATED
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in
            ["id"]
        )

        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_all"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
        assert body.get("metadata").get("id") in [i.get("id") for i in r_data]


def test_create_instance_invalid_payload(app, client, api_key_authentication) -> None:
    body: dict = {
        "nameBro": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pemPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.BAD_REQUEST


def test_create_instance_non_existent_flavour(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "LEL",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.NOT_FOUND


def test_create_instance_non_existent_image(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "LOL",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.NOT_FOUND


def test_create_instance_non_existent_sec_groups(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    app.config["IGNORE_SEC_GROUP_NOT_FOUND_ERRORS"] = False

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.NOT_FOUND

    app.config["IGNORE_SEC_GROUP_NOT_FOUND_ERRORS"] = True


def test_instance_quota_exceedance_instance_creation(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    prev_max_inst: int = app.config["MAX_INSTANCES_ALLOCATED"]
    app.config["MAX_INSTANCES_ALLOCATED"] = 1

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.CONFLICT

    app.config["MAX_INSTANCES_ALLOCATED"] = prev_max_inst


def test_memory_quota_exceedance_instance_creation(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    prev_max_ram: float = app.config["MAX_RAM_ALLOCATED"]
    app.config["MAX_RAM_ALLOCATED"] = 1

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.CONFLICT

    app.config["MAX_RAM_ALLOCATED"] = prev_max_ram


def test_cpu_quota_exceedance_instance_creation(app, client, api_key_authentication) -> None:
    body: dict = {
        "name": "test2-sample",
        "imageId": "test-image-1",
        "flavourId": "test-flavour-1",
        "securityGroups": ["default", "ssh", "..."],
        "metadata": {
            "id": "1234",
            "uid": "1001",
            "owner": "jdoe",
            "screenWidth": "1920",
            "screenHeight": "1080",
            "keyboardLayout": "en-gb-qwerty",
            "instruments": "D16,IN5",
            "proposals": "TEST-1234,TEST-5678",
            "pamPublicKey": "-----BEGIN PUBLIC KEY-----..."
        },
        "bootCommand": "ASD"
    }

    prev_max_cpus: float = app.config["MAX_CORES_ALLOCATED"]
    app.config["MAX_CORES_ALLOCATED"] = 1

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.create_instance"),
                                      headers=api_key_authentication, json=body)
        assert r.status_code == HTTPStatus.CONFLICT

    app.config["MAX_CORES_ALLOCATED"] = prev_max_cpus
