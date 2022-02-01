import copy
import json
from splash.test.testing_utils import equal_dicts

import pytest


def create_resource(api_url_root, splash_client, token_header, resource):
    url_path = api_url_root + "/references"
    return splash_client.post(url_path, json=copy.deepcopy(resource), headers=token_header)


# TODO: Test the put functions
@pytest.mark.usefixtures("splash_client", "token_header")
def test_flask_crud(api_url_root, splash_client, token_header):
    url_path = api_url_root + "/references"
    post_resp = splash_client.post(url_path, data="{", headers=token_header)
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    reference_1["uid"] = "test"
    post_resp = splash_client.post(
        url_path, json=copy.deepcopy(reference_1), headers=token_header
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
        url_path, json=copy.deepcopy(reference_1), headers=token_header
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



@pytest.mark.skip(reason="mongomock does not implement the '$text' operator yet")
def test_search(api_url_root, splash_client, token_header):
    url = api_url_root + "/references"

    post_resp = splash_client.post(
        url, json=copy.deepcopy(reference_2), headers=token_header
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


def test_etag_functionality(
    api_url_root, splash_client, token_header
):
    url_path = api_url_root + "/references"
    post_resp = splash_client.post(
        url_path, json=copy.deepcopy(reference_3), headers=token_header
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
        json=copy.deepcopy(reference_4),
        headers={"If-Match": etag1, **token_header},
    )
    assert (
        put_resp1.status_code == 200
    ), f"{put_resp1.status_code}: response is {put_resp1.content}"

    get_resp2 = splash_client.get(url_path + "/uid/" + uid, headers=token_header)
    etag2 = get_resp2.json()["splash_md"]["etag"]
    assert etag2 != etag1

    put_resp2 = splash_client.put(
        url_path + "/uid/" + uid,
        json=copy.deepcopy(reference_3),
        headers={"If-Match": etag1, **token_header},
    )
    assert (
        put_resp2.status_code == 412
    ), f"{put_resp2.status_code}: response is {put_resp2.content}"
    assert put_resp2.json()["etag"] == etag2
    assert put_resp2.json()["err"] == "etag_mismatch_error"

    get_resp3 = splash_client.get(url_path + "/uid/" + uid, headers=token_header)
    # Ensure that no changes were made to the document
    assert get_resp3.json() == get_resp2.json()


def test_retrieve_by_DOI(api_url_root, splash_client, token_header):
    url_path = api_url_root + "/references"
    post_resp1 = create_resource(api_url_root, splash_client, token_header, reference_5)
    assert (
        post_resp1.status_code == 200
    ), f"{post_resp1.status_code}: response is {post_resp1.content}"

    create_resource(api_url_root, splash_client, token_header, reference_7)
    get_resp1 = splash_client.get(
        url_path + "/doi/" + reference_5["DOI"], headers=token_header
    )
    assert post_resp1.json()['uid'] == get_resp1.json()[0]['uid']
    equal_dicts(reference_5, get_resp1.json()[0], ignore_keys=['uid', 'splash_md'])
    assert len(get_resp1.json()) == 1

    post_resp2 = create_resource(api_url_root, splash_client, token_header, reference_6)
    get_resp2 = splash_client.get(
        url_path + "/doi/" + reference_6["DOI"], headers=token_header
    )

    assert (
        post_resp2.status_code == 200
    ), f"{post_resp2.status_code}: response is {post_resp2.content}"

    assert any(post_resp2.json()['uid'] == page['uid'] for page in get_resp2.json())
    assert any(post_resp1.json()['uid'] == page['uid'] for page in get_resp2.json())
    assert len(get_resp2.json()) == 2

@pytest.mark.skip(reason="mongomock does not do case insensitive collation yet")
def test_case_insensitivity(api_url_root, splash_client, token_header):
    url_path = api_url_root + "/references"
    post_resp1 = create_resource(api_url_root, splash_client, token_header, reference_8)
    assert (
        post_resp1.status_code == 200
    ), f"{post_resp1.status_code}: response is {post_resp1.content}"

    post_resp2 = create_resource(api_url_root, splash_client, token_header, reference_9)
    assert (
        post_resp2.status_code == 200
    ), f"{post_resp2.status_code}: response is {post_resp2.content}"

    get_resp = splash_client.get(
        url_path + "/doi/" + reference_8["DOI"], headers=token_header
    )
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 2
    
    assert any(equal_dicts(reference_8, page, ignore_keys=["uid", "splash_md"], return_value=True) for page in get_resp.json())
    assert any(equal_dicts(reference_9, page, ignore_keys=["uid", "splash_md"], return_value=True) for page in get_resp.json())


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

reference_3 = {
    "DOI": "10.5406/jrfff",
    "title": "Test3",
    "author": [
        {"family": "The Grey", "given": "Gandalf"},
        {"family": "The White", "given": "Saruman"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}

reference_4 = {
    "DOI": "10.5406/jrfff",
    "title": "Test4",
    "author": [
        {"family": "The Grey", "given": "Gandalf"},
        {"family": "The White", "given": "Saruman"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}



reference_5 = {
    "DOI": "10.xx/xx",
    "title": "Test5",
    "author": [
        {"family": "Baggins", "given": "Frodo"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}

reference_6 = {
    "DOI": "10.xx/xx",
    "title": "Test6",
    "author": [
        {"family": "Baggins", "given": "Bilbo"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}


reference_7 = {
    "DOI": "10.ff/ff",
    "title": "Test7",
    "author": [
        {"family": "Baggins", "given": "Bilbo"},
    ],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}

reference_8 = {
    "DOI": "10.rrr/rrr",
    "title": "Test8",
}

reference_9 = {
    "title": "Test9",
    "DOI": "10.RRR/RRR"
}