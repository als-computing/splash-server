import copy
import json

import pytest

from .testing_utils import (
    equal_dicts,
    generic_test_api_crud,
    generic_test_etag_functionality,
)


@pytest.mark.usefixtures("splash_client", "token_header")
def test_flask_crud_user(api_url_root, splash_client, token_header):
    generic_test_api_crud(
        new_page, api_url_root + "/pages", splash_client, token_header
    )


def test_etag_functionality(api_url_root, splash_client, token_header):
    generic_test_etag_functionality(
        new_page, api_url_root + "/pages", splash_client, token_header
    )


def test_no_empty_strings(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    post_resp = splash_client.post(
        url, data=json.dumps(empty_string_title), headers=token_header
    )
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"
    post_resp = splash_client.post(
        url, json=copy.deepcopy(empty_string_documentation), headers=token_header
    )
    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"


def test_retrieve_by_type(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    post_resp1 = splash_client.post(
        url,
        json={
            "title": "Maiar",
            "page_type": "mythical_animals",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    assert (
        post_resp1.status_code == 200
    ), f"{post_resp1.status_code}: response is {post_resp1.content}"
    post_resp2 = splash_client.post(
        url,
        json={
            "title": "Troll",
            "page_type": "mythical_animals",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    assert (
        post_resp2.status_code == 200
    ), f"{post_resp2.status_code}: response is {post_resp2.content}"
    post_resp3 = splash_client.post(
        url,
        json={
            "title": "Wand",
            "page_type": "mythical_items",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    assert (
        post_resp3.status_code == 200
    ), f"{post_resp3.status_code}: response is {post_resp3.content}"

    response = splash_client.get(
        url + "/page_type/mythical_animals", headers=token_header
    )
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 2
    assert any(page["title"] == "Maiar" for page in resp_obj)
    assert any(page["title"] == "Troll" for page in resp_obj)


def test_versioning(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    post_resp = splash_client.post(
        url,
        json={
            "title": "Drake",
            "page_type": "mythical_animals",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    uid = post_resp.json()["uid"]
    response = splash_client.get(url + "/" + uid, headers=token_header)
    assert response.json()["splash_md"]["version"] == 1
    assert response.json()["title"] == "Drake"
    assert post_resp.json()["splash_md"] == response.json()["splash_md"]

    put_resp = splash_client.put(
        url + "/" + uid,
        json={
            "title": "Drake/Dragon",
            "page_type": "mythical_animals",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    response = splash_client.get(url + "/" + uid, headers=token_header)
    assert response.json()["splash_md"]["version"] == 2
    assert response.json()["title"] == "Drake/Dragon"
    assert put_resp.json()["splash_md"] == response.json()["splash_md"]

    response = splash_client.get(url, headers=token_header)
    data = response.json()
    # Make sure that the old version does not get returned in the list of pages
    assert all(page["title"] != "Drake" for page in data)
    # make sure that the current version is in the returned list of pages
    assert any(
        page["title"] == "Drake/Dragon" and page["splash_md"]["version"] == 2
        for page in data
    )

    response = splash_client.get(url + "/" + uid + "?version=1", headers=token_header)
    data = response.json()
    assert data["splash_md"]["version"] == 1
    assert data["title"] == "Drake"

    response = splash_client.get(url + "/" + uid + "?version=2", headers=token_header)
    data = response.json()
    assert data["splash_md"]["version"] == 2
    assert data["title"] == "Drake/Dragon"

    response = splash_client.get(url + "/" + uid + "?version=1.5", headers=token_header)
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"

    response = splash_client.get(url + "/" + uid + "?version=0", headers=token_header)
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"

    response = splash_client.get(url + "/" + uid + "?version=3", headers=token_header)
    assert (
        response.status_code == 404
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "version not found"

    put_resp = splash_client.put(
        url + "/" + "does not exist",
        json={
            "title": "Drake/Dragon",
            "page_type": "mythical_animals",
            "documentation": "Hello",
            "references": [],
        },
        headers=token_header,
    )
    assert (
        put_resp.status_code == 404
    ), f"{put_resp.status_code}: response is {put_resp.content}"
    assert put_resp.json()["detail"] == "object not found"

    response = splash_client.get(url + "/" + "does not exist", headers=token_header)
    assert (
        response.status_code == 404
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "object not found"

    response = splash_client.get(
        url + "/" + "doesnotexist?version=1", headers=token_header
    )
    assert (
        response.status_code == 404
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "object not found"

    put_resp = splash_client.put(
        url + "/" + uid,
        json={
            "title": "Drake/Dragon",
            "page_type": "mythical_animals",
            "documentation": "test",
            "document_version": 3,
            "references": [],
        },
        headers=token_header,
    )

    assert (
        put_resp.status_code == 422
    ), f"{put_resp.status_code}: response is {put_resp.content}"

    post_resp = splash_client.post(
        url,
        json={
            "title": "Drake/Dragon",
            "page_type": "mythical_animals",
            "documentation": "test",
            "document_version": 3,
            "references": [],
        },
        headers=token_header,
    )

    assert (
        post_resp.status_code == 422
    ), f"{post_resp.status_code}: response is {post_resp.content}"


def test_retrieve_num_versions(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    post_resp = splash_client.post(
        url,
        json={
            "title": "Beethoven's 5th",
            "page_type": "songs",
            "documentation": "test",
            "references": [],
        },
        headers=token_header,
    )
    uid = post_resp.json()["uid"]
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 1

    response = splash_client.put(
        url + "/" + uid,
        json={
            "title": "Schicksals-Sinfonie",
            "page_type": "songs",
            "documentation": "test",
            "references": [],
        },
        headers=token_header,
    )
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 2

    response = splash_client.put(
        url + "/" + uid,
        json={
            "title": "Schicksals-Sinfonie, Beethoven's 5th",
            "page_type": "songs",
            "documentation": "test",
            "references": [],
        },
        headers=token_header,
    )
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 3

    response = splash_client.get(
        url + "/num_versions/" + "this_uid_is_non_existent", headers=token_header
    )
    assert (
        response.status_code == 404
    ), f"{response.status_code}: response is {response.content}"


def test_archive_and_restore(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    archive_req = {"archive_action": "archive"}
    restore_req = {"archive_action": "restore"}
    doc = {
            "title": "Blue Jay",
            "page_type": "birds",
            "documentation": "This is a bird that is blue",
            "references": [],
        }

    post_resp = splash_client.post(
        url,
        json=copy.deepcopy(doc),
        headers=token_header,
    )

    assert post_resp.status_code == 200

    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=archive_req, headers=token_header
    )
    assert patch_resp.status_code == 200
    get_resp = splash_client.get(
        url + "/archived",
        headers=token_header,
    )
    assert get_resp.status_code == 200, f'the response is {get_resp.json()}'
    assert len(get_resp.json()) == 1
    equal_dicts(get_resp.json()[0], doc, ignore_keys=["uid", "splash_md"])
    assert patch_resp.json()['splash_md'] == get_resp.json()[0]['splash_md']
    assert patch_resp.json()['uid'] == post_resp.json()['uid']

    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=restore_req, headers=token_header
    )
    assert patch_resp.status_code == 200
    get_resp = splash_client.get(
        url + "/archived",
        headers=token_header,
    )
    assert len(get_resp.json()) == 0
    doc_resp = splash_client.get(
        url + "/" + post_resp.json()["uid"], headers=token_header
    )
    assert doc_resp.status_code == 200
    equal_dicts(doc_resp.json(), doc, ignore_keys=["uid", "splash_md"])
    assert patch_resp.json()['splash_md'] == doc_resp.json()['splash_md']
    assert patch_resp.json()['uid'] == post_resp.json()['uid']


def test_bad_archive_req(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    bad_req = {"archive_action": "action_does_not_exist"}
    post_resp = splash_client.post(
        url,
        json={
            "title": "Blue Jay",
            "page_type": "birds",
            "documentation": "This is a bird that is blue",
            "references": [],
        },
        headers=token_header,
    )

    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=bad_req, headers=token_header
    )
    assert patch_resp.status_code == 422
    archives = splash_client.get(url + "/archived", headers=token_header).json()
    assert len(archives) == 0


def test_archive_and_restore_conflict(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    archive_req = {"archive_action": "archive"}
    restore_req = {"archive_action": "restore"}
    doc = {
        "title": "Blue Jay",
        "page_type": "birds",
        "documentation": "This is a bird that is blue",
        "references": [],
    }

    post_resp = splash_client.post(
        url,
        json=copy.deepcopy(doc),
        headers=token_header,
    )
    assert post_resp.status_code == 200
    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=restore_req, headers=token_header
    )
    assert patch_resp.status_code == 409, f'response is {patch_resp.json()}'
    assert patch_resp.json()["err"] == "not_archived"
    get_resp = splash_client.get(
        url + "/archived",
        headers=token_header,
    )
    assert len(get_resp.json()) == 0

    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=archive_req, headers=token_header
    )
    assert patch_resp.status_code == 200
    patch_resp = splash_client.patch(
        url + "/" + post_resp.json()["uid"], json=archive_req, headers=token_header
    )
    assert patch_resp.status_code == 409
    assert patch_resp.json()["err"] == "already_archived"
    get_resp = splash_client.get(
        url + "/archived",
        headers=token_header,
    )
    assert len(get_resp.json()) == 1


new_page = {
    "title": "Boron",
    "page_type": "compound",
    "documentation": "- Naturally occurring in the environment\n\t - Seawater concentration around 5 mg/L [[1]](#1)\
                \n - Toxicity\n\t - boron has an extremely narrow concentration range between deficiency and toxicity \
                in some plants [[2]](#2) and it has been shown to suppress plant growth [[3]](#3) and immune response \
                in several crops [[4]](#4) .\n - Small, neutral solute\n\t - Boric acid is a small solute, with an \
                estimated Stokes radius of 1.6 Å [[5]](#5) , compared to 1.8 Å and 1.2 Å for sodium and chloride, \
                respectively [[6]](#6) .\n\t - The Stokes radius of borate has been estimated as 2.6 Å [[7]](#7) .",
    "references": [{"uid": "ffff-ffff-fffff-fffff", "in_text": False}],
}

empty_string_documentation = {
    "title": "Boron",
    "page_type": "compound",
    "documentation": "",
    "references": [],
}
empty_string_title = {
    "title": "",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": " - Landsman, Lawler, Katz (2020). Application of electrodialysis pretreatment to enhance boron \
                    removal and reduce fouling during nanofiltration/reverse osmosis",
    "references": [],
}
