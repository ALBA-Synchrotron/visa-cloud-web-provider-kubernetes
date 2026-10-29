import time
from http import HTTPStatus

from flask import url_for
from werkzeug.test import TestResponse

ENDPOINT_NAME_PREFIX: str = "v1.instance"


def wait_until_not_found(client, url: str, headers: dict, timeout: float = 30, interval: float = 0.3):
    deadline = time.monotonic() + timeout
    r = None
    while time.monotonic() < deadline:
        r = client.get(url, headers=headers)
        if r.status_code == HTTPStatus.NOT_FOUND:
            return r
        time.sleep(interval)
    raise AssertionError(f"Instance still present after {timeout}s: {r.get_json()}")


def test_start_instance(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.start_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)


def test_start_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just_invented_this_original_thing"

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.start_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.NOT_FOUND
        assert isinstance(r_data, dict)


def test_stop_instance(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.stop_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)


def test_stop_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just_invented_this_original_thing"

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.stop_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.NOT_FOUND
        assert isinstance(r_data, dict)


def test_restart_instance(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.restart_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.OK
        assert isinstance(r_data, dict)


def test_restart_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just_invented_this_original_thing"

    with app.test_request_context():
        r: TestResponse = client.post(url_for(f"{ENDPOINT_NAME_PREFIX}.restart_instance",
                                              instance_id=test_instance_name),
                                      headers=api_key_authentication)
        r_data: list = r.get_json()

        assert r.status_code == HTTPStatus.NOT_FOUND
        assert isinstance(r_data, dict)


def test_delete_instance(app, client, api_key_authentication, test_instance, reset_instances) -> None:
    test_instance_name: str = test_instance.get("metadata").get("name")

    with app.test_request_context():
        r = client.delete(url_for(f"{ENDPOINT_NAME_PREFIX}.delete_instance",
                                  instance_id=test_instance_name),
                          headers=api_key_authentication)
        assert r.status_code == HTTPStatus.OK

        get_url = url_for(f"{ENDPOINT_NAME_PREFIX}.get_by_name", instance_id=test_instance_name)
        r = wait_until_not_found(client, get_url, api_key_authentication)
        assert r.status_code == HTTPStatus.NOT_FOUND


def test_delete_non_existent_instance(app, client, api_key_authentication) -> None:
    test_instance_name: str = "just-invented"

    with app.test_request_context():
        r: TestResponse = client.delete(url_for(f"{ENDPOINT_NAME_PREFIX}.delete_instance",
                                                instance_id=test_instance_name),
                                        headers=api_key_authentication)

        assert r.status_code == HTTPStatus.NOT_FOUND
