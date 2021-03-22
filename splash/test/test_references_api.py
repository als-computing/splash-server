from .testing_utils import equal_dicts, MockSecurityScopes
from ..api.auth import get_current_user
import pytest
import json


# TODO: Test the put functions
@pytest.mark.usefixtures("splash_client", "token_header", "token_header2")
def test_flask_crud(api_url_root, splash_client, token_header):
    url_path = api_url_root + "/references"
    post_resp = splash_client.post(url_path, data="{", headers=token_header)
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    reference_1["uid"] = "test"
    post_resp = splash_client.post(
        url_path, data=json.dumps(reference_1), headers=token_header
    )
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    # response = splash_client.put(url_path + "/sample_uid",
    #                              data=json.dumps(reference_1),
    #                              headers=token_header)
    # assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    reference_1.pop("uid")
    post_resp = splash_client.post(
        url_path, data=json.dumps(reference_1), headers=token_header
    )
    assert (
        post_resp.status_code == 200
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    response_dict = post_resp.json()
    new_uid = response_dict["uid"]
    assert new_uid
    assert response_dict["splash_md"] == post_resp.json()["splash_md"]

    # retreive all
    response = splash_client.get(url_path, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    response_dict = response.json()
    assert len(response_dict) > 0

    # retrive one
    response = splash_client.get(url_path + "/uid/" + new_uid, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"

    response = splash_client.get(
        url_path + "/doi/" + reference_1["DOI"], headers=token_header
    )
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"


def test_etag_functionality(
    api_url_root, splash_client, token_header, token_header2
):
    url_path = api_url_root + "/references"
    post_resp = splash_client.post(
        url_path, data=json.dumps(reference_1), headers=token_header
    )
    assert (
        post_resp.status_code == 200
    ), f"{post_resp.status_code}: response is {post_resp.content}"
    assert len(post_resp.json()["splash_md"]["etag"]) > 0
    uid = post_resp.json()["uid"]

    get_resp1 = splash_client.get(url_path + "/uid/" + uid, headers=token_header)

    etag1 = get_resp1.json()["splash_md"]["etag"]
    assert len(etag1) > 0

    put_resp1 = splash_client.put(
        url_path + "/uid/" + uid,
        data=json.dumps(reference_2),
        headers={"If-Match": etag1, **token_header2},
    )
    assert (
        put_resp1.status_code == 200
    ), f"{put_resp1.status_code}: response is {put_resp1.content}"

    get_resp2 = splash_client.get(url_path + "/uid/" + uid, headers=token_header)
    assert get_resp2.json()["splash_md"]["etag"] != etag1

    put_resp2 = splash_client.put(
        url_path + "/uid/" + uid,
        data=json.dumps(reference_1),
        headers={"If-Match": etag1, **token_header},
    )
    assert (
        put_resp2.status_code == 412
    ), f"{put_resp2.status_code}: response is {put_resp2.content}"
    assert put_resp2.json()["document"] == get_resp2.json()
    equal_dicts(put_resp2.json()["last_editor"], get_current_user(MockSecurityScopes(), token_header2).dict(), ignore_keys=["uid", "splash_md"])

    get_resp3 = splash_client.get(url_path + "/uid/" + uid, headers=token_header)
    # Ensure that no changes were made to the document
    assert get_resp3.json() == get_resp2.json()


def test_search(api_url_root, splash_client, token_header):
    url = api_url_root + "/references"

    post_resp = splash_client.post(
        url, data=json.dumps(reference_2), headers=token_header
    )
    assert (
        post_resp.status_code == 200
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    response = splash_client.get(url + "?search=Middle", headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 2
    assert any(reference_1["title"] == page["title"] for page in resp_obj)
    assert any(reference_2["title"] == page["title"] for page in resp_obj)

    response = splash_client.get(url + "?search=Gandalf", headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 2
    assert any(reference_1["title"] == page["title"] for page in resp_obj)
    assert any(reference_2["title"] == page["title"] for page in resp_obj)

    response = splash_client.get(url + "?search=Wizards", headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 1
    assert resp_obj[0]["title"] == reference_2["title"]

    response = splash_client.get(url + "?search=ecological", headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 1
    assert resp_obj[0]["title"] == reference_1["title"]

    # Test to make sure that regex is escaped
    response = splash_client.get(url + "?search=^", headers=token_header)
    assert len(response.json()) == 0


reference_1 = {
    "DOI": "10.5406/jfilmvideo.67.3-4.0079",
    "title": "The ecological relationship between Mordor and Middle Earth: A life systems analysis",
    "author": [
        {"family": "The Grey", "given": "Gandalf"},
        {"family": "The White", "given": "Saruman"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}

reference_2 = {
    "DOI": "10.5406/mordor",
    "title": "The Effects of Sauron's Ring on Middle Earth: A meta-analysis.",
    "author": [{"family": "The Grey", "given": "Gandalf"}, {"literal": "Wizards Inc."}],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}
