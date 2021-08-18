import copy
import json


def generic_test_api_crud(sample_new_object, url_path, splash_client, token_header):
    post_resp = splash_client.post(url_path, data="{", headers=token_header)
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    sample_new_object["uid"] = "test"
    post_resp = splash_client.post(
        url_path, data=json.dumps(sample_new_object), headers=token_header
    )
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    # response = splash_client.get(url_path + '/' + "DOES NOT EXIST", headers=token_header)
    # assert response.status_code == 404, f"{response.status_code}: response is {response.content}"

    # response = splash_client.put(url_path + "/sample_uid",
    #                              data=json.dumps(sample_new_object),
    #                              headers=token_header)
    # assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    sample_new_object.pop("uid")
    post_resp = splash_client.post(
        url_path, json=copy.deepcopy(sample_new_object), headers=token_header
    )
    assert (
        post_resp.status_code == 200
    ), f"{post_resp.status_code}: response is {post_resp.content}"

    post_resp_dict = post_resp.json()
    new_uid = post_resp_dict["uid"]
    assert new_uid

    # retreive all
    response = splash_client.get(url_path, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    response_dict = response.json()
    assert len(response_dict) > 0

    # retrive one
    response = splash_client.get(url_path + "/" + new_uid, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"

    assert post_resp.json()["splash_md"] == response.json()["splash_md"], f'{post_resp.json()["splash_md"]} is not {response.json()["splash_md"]}'
    # TODO: TEST put api

    # response = splash_client.put(url_path + '/' + new_uid, data=json.dumps(sample_new_object), headers=token_header)
    # assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    # we used to validate more, but with the switch tn FastAPI, new object models aren't the same
    # as existing object models
    # sample_new_object_returned = response.json()
    # sample_new_object['uid'] = sample_new_object_returned['uid']  # now let's give the generated uid so we can compare
    # assert sample_new_object_returned == sample_new_object


def generic_test_etag_functionality(
    sample_new_object, url_path, splash_client, token_header
):
    post_resp = splash_client.post(
        url_path, json=sample_new_object, headers=token_header
    )
    assert (
        post_resp.status_code == 200
    ), f"{post_resp.status_code}: response is {post_resp.content}"
    assert len(post_resp.json()["splash_md"]["etag"]) > 0
    post_resp.json()["splash_md"]["etag"] is str
    uid = post_resp.json()["uid"]

    get_resp1 = splash_client.get(url_path + "/" + uid, headers=token_header)

    etag1 = get_resp1.json()["splash_md"]["etag"]
    assert len(etag1) > 0

    put_resp1 = splash_client.put(
        url_path + "/" + uid,
        json=copy.deepcopy(sample_new_object),
        headers={"If-Match": etag1, **token_header},
    )
    assert (
        put_resp1.status_code == 200
    ), f"{put_resp1.status_code}: response is {put_resp1.content}"

    get_resp2 = splash_client.get(url_path + "/" + uid, headers=token_header)
    etag2 = get_resp2.json()["splash_md"]["etag"]
    assert etag2 != etag1

    put_resp2 = splash_client.put(
        url_path + "/" + uid,
        json=copy.deepcopy(sample_new_object),
        headers={"If-Match": etag1, **token_header},
    )
    assert (
        put_resp2.status_code == 412
    ), f"{put_resp2.status_code}: response is {put_resp2.content}"

    assert put_resp2.json()["err"] == "etag_mismatch_error"
    assert put_resp2.json()["etag"] == etag2

    get_resp3 = splash_client.get(url_path + "/" + uid, headers=token_header)
    # Make sure that the document was not changed
    assert get_resp3.json() == get_resp2.json()
    assert put_resp2.json()['splash_md'] == get_resp3.json()['splash_md'], f'{put_resp2.json()["splash_md"]} is not {get_resp3.json()["splash_md"]}'




# Utility function for asserting that dicts are equal, excluding specific keys
# https://stackoverflow.com/questions/10480806/compare-dictionaries-ignoring-specific-keys
def equal_dicts(d1, d2, ignore_keys=[]):
    d1_filtered = {k: v for k, v in d1.items() if k not in ignore_keys}
    d2_filtered = {k: v for k, v in d2.items() if k not in ignore_keys}
    assert d1_filtered == d2_filtered, f"{d1_filtered} does not equal {d2_filtered}"
