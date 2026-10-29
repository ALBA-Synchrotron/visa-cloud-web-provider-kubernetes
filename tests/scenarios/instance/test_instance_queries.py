from http import HTTPStatus

from flask import url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.instance"


def test_get_all_instances(app, client, api_key_authentication, instances_list, reset_instances) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_all"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
        for i in r_data:
            assert isinstance(i, dict)
            assert all(
                key in i.keys()
                for key in
                ["id", "name", "state", "flavourId", "imageId", "createdAt", "address", "securityGroups", "fault"]
            )
            assert all(
                key in i["fault"].keys()
                for key in
                ["message", "code", "details", "createdAt"]
            )
        assert len(instances_list) == len(r_data)


def test_get_instance_by_id(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in
            ["id", "name", "state", "flavourId", "imageId", "createdAt", "address", "securityGroups", "fault"]
        )
        assert all(
            key in r_data["fault"].keys()
            for key in
            ["message", "code", "details", "createdAt"]
        )


def test_get_non_existent_instance_by_id(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just_invented_this_original_thing"

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.NOT_FOUND
        assert isinstance(r_data, dict)


def test_get_instance_ip_by_id(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_ip_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)
        assert all(
            key in r_data.keys()
            for key in
            ["id", "address"]
        )
        assert isinstance(r_data["address"], str)


def test_get_non_existent_instance_ip_by_id(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just_invented_this_original_thing"

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_ip_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.NOT_FOUND
        assert isinstance(r_data, dict)


def test_get_all_instance_identifiers(app, client, api_key_authentication, instances_list, reset_instances) -> None:
    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_all_identifiers"),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
        for i in r_data:
            assert isinstance(i, dict)
            assert all(
                key in i.keys()
                for key in
                ["id"]
            )
        assert len(instances_list) == len(r_data)
