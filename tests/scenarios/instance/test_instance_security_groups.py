from http import HTTPStatus

from flask import url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.instance"


def test_get_instance_sec_groups_by_id(app, client, api_key_authentication, test_instance) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_security_groups_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, list)
        assert sorted(r_data) == sorted([i.get("name") for i in test_instance.get("spec").get("securityGroups")])


def test_add_sec_group_to_instance(app, client, api_key_authentication, test_instance) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    body: dict = {"name": "test-sec-group"}

    with app.test_request_context():
        prev_sec_groups: list = sorted([i.get("name") for i in test_instance.get("spec").get("securityGroups")])
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.add_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)

        assert r.status_code == HTTPStatus.OK

        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()
        assert r.status_code == HTTPStatus.OK
        assert prev_sec_groups != sorted(r_data)


def test_add_sec_group_to_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just-invented-this"

    body: dict = {"name": "test-sec-group"}

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.add_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)

        assert r.status_code == HTTPStatus.NOT_FOUND


def test_invalid_payload_add_sec_group_to_instance(app, client, api_key_authentication, test_instance) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    body: dict = {"namessss": "test-sec-group"}

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.add_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)

        assert r.status_code == HTTPStatus.BAD_REQUEST


def test_remove_sec_group_from_instance(app, client, api_key_authentication, test_instance) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    body: dict = {"name": test_instance.get("spec").get("securityGroups")[0].get("name")}

    with app.test_request_context():
        prev_sec_groups: list = sorted([i.get("name") for i in test_instance.get("spec").get("securityGroups")])
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.remove_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)
        cur_sec_groups = sorted([i.get("name") for i in test_instance.get("spec").get("securityGroups")])

        assert r.status_code == HTTPStatus.OK
        assert prev_sec_groups != cur_sec_groups

        r: TestResponse = client.get(url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name",
                                             instance_id=test_instance_name),
                                     headers=api_key_authentication)
        r_data: list = r.get_json()
        assert r.status_code == HTTPStatus.OK
        assert prev_sec_groups != sorted(r_data)


def test_remove_sec_group_from_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just-invented-this"

    body: dict = {"name": "test-sec-group"}

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.remove_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)

        assert r.status_code == HTTPStatus.NOT_FOUND


def test_invalid_payload_remove_sec_group_from_instance(app, client, api_key_authentication, test_instance) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    body: dict = {"namessss": "test-sec-group"}

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.remove_security_group",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication, json=body)

        assert r.status_code == HTTPStatus.BAD_REQUEST
