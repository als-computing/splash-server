import pytest
import json
from .testing_utils import generic_test_api_crud



@pytest.mark.usefixtures("splash_client", "token_header")
def test_flask_crud_user(api_url_root, splash_client, token_header):
    generic_test_api_crud(
        new_page, api_url_root + "/pages", splash_client, token_header
    )


def test_no_empty_strings(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    response = splash_client.post(
        url, data=json.dumps(empty_string_metadata_title), headers=token_header
    )
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url, data=json.dumps(empty_string_metadata_text), headers=token_header
    )
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url, data=json.dumps(empty_string_section_title), headers=token_header
    )
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url, data=json.dumps(empty_string_section_text), headers=token_header
    )
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url, data=json.dumps(empty_string_title), headers=token_header
    )
    assert (
        response.status_code == 422
    ), f"{response.status_code}: response is {response.content}"


def test_retrieve_by_type(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Maiar",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Troll",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"
    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Wand",
                "page_type": "mythical_items",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    assert (
        response.status_code == 200
    ), f"{response.status_code}: response is {response.content}"

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
    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Drake",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    uid = response.json()["uid"]
    response = splash_client.get(url + "/" + uid, headers=token_header)
    assert response.json()["document_version"] == 1
    assert response.json()["title"] == "Drake"

    splash_client.put(
        url + "/" + uid,
        data=json.dumps(
            {
                "title": "Drake/Dragon",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    response = splash_client.get(url + "/" + uid, headers=token_header)
    assert response.json()["document_version"] == 2
    assert response.json()["title"] == "Drake/Dragon"

    response = splash_client.get(url, headers=token_header)
    data = response.json()
    # Make sure that the old version does not get returned in the list of pages
    assert all(page["title"] != "Drake" for page in data)
    # make sure that the current version is in the returned list of pages
    assert any(page["title"] == "Drake/Dragon" and page["document_version"] == 2 for page in data)

    response = splash_client.get(url + "/" + uid + "?version=1", headers=token_header)
    data = response.json()
    assert data["document_version"] == 1
    assert data["title"] == "Drake"

    response = splash_client.get(url + "/" + uid + "?version=2", headers=token_header)
    data = response.json()
    assert data["document_version"] == 2
    assert data["title"] == "Drake/Dragon"

    response = splash_client.get(url + "/" + uid + "?version=1.5", headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"
    
    response = splash_client.get(url + "/" + uid + "?version=0", headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    response = splash_client.get(url + "/" + uid + "?version=3", headers=token_header)
    assert response.status_code == 404, f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "version not found"

    response = splash_client.put(url + "/" + "does not exist", data=json.dumps({
                "title": "Drake/Dragon",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
            }), headers=token_header)
    assert response.status_code == 404, f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "object not found"

    response = splash_client.get(url + "/" + "does not exist", headers=token_header)
    assert response.status_code == 404, f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "object not found"
    
    response = splash_client.get(url + "/" + "doesnotexist?version=1", headers=token_header)
    assert response.status_code == 404, f"{response.status_code}: response is {response.content}"
    assert response.json()["detail"] == "object not found"

    response = splash_client.put(
        url + "/" + uid,
        data=json.dumps(
            {
                "title": "Drake/Dragon",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
                "document_version": 3
            }
        ),
        headers=token_header,
    )

    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Drake/Dragon",
                "page_type": "mythical_animals",
                "metadata": [],
                "documentation": [],
                "document_version": 3
            }
        ),
        headers=token_header,
    )

    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

def test_retrieve_num_versions(api_url_root, splash_client, token_header):
    url = api_url_root + "/pages"
    response = splash_client.post(
        url,
        data=json.dumps(
            {
                "title": "Beethoven's 5th",
                "page_type": "songs",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    uid = response.json()["uid"]
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 1

    response = splash_client.put(
        url + "/" + uid,
        data=json.dumps(
            {
                "title": "Schicksals-Sinfonie",
                "page_type": "songs",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 2

    response = splash_client.put(
        url + "/" + uid,
        data=json.dumps(
            {
                "title": "Schicksals-Sinfonie, Beethoven's 5th",
                "page_type": "songs",
                "metadata": [],
                "documentation": [],
            }
        ),
        headers=token_header,
    )
    response = splash_client.get(url + "/num_versions/" + uid, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    assert response.json()["number"] == 3

    response = splash_client.get(url + "/num_versions/" + "this_uid_is_non_existent", headers=token_header)
    assert response.status_code == 404, f"{response.status_code}: response is {response.content}"



new_page = {
    "title": "Boron",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": {
        "sections": [
            {
                "title": "Relevance to M-WET:",
                "text": "- Naturally occurring in the environment\n\t - Seawater concentration around 5 mg/L [[1]](#1)\
                \n - Toxicity\n\t - boron has an extremely narrow concentration range between deficiency and toxicity \
                in some plants [[2]](#2) and it has been shown to suppress plant growth [[3]](#3) and immune response \
                in several crops [[4]](#4) .\n - Small, neutral solute\n\t - Boric acid is a small solute, with an \
                estimated Stokes radius of 1.6 Å [[5]](#5) , compared to 1.8 Å and 1.2 Å for sodium and chloride, \
                respectively [[6]](#6) .\n\t - The Stokes radius of borate has been estimated as 2.6 Å [[7]](#7) .",
            },
        ]
    },
}

empty_string_title = {
    "title": "",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": {
        "sections": [
            {
                "title": "Internal publications",
                "text": " - Landsman, Lawler, Katz (2020). Application of electrodialysis pretreatment to enhance boron \
                    removal and reduce fouling during nanofiltration/reverse osmosis",
            }
        ]
    },
}

empty_string_metadata_title = {
    "title": "Boron",
    "page_type": "compound",
    "metadata": [{"title": "", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": {
        "sections": [
            {
                "title": "Internal publications",
                "text": " - Landsman, Lawler, Katz (2020). Application of electrodialysis pretreatment to enhance boron \
                removal and reduce fouling during nanofiltration/reverse osmosis",
            }
        ]
    },
}

empty_string_metadata_text = {
    "title": "",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": ""}],
    "documentation": {
        "sections": [
            {
                "title": "Internal publications",
                "text": " - Landsman, Lawler, Katz (2020). Application of electrodialysis pretreatment to enhance boron \
                    removal and reduce fouling during nanofiltration/reverse osmosis",
            }
        ]
    },
}

empty_string_section_title = {
    "title": "Boron",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": {
        "sections": [
            {
                "title": "",
                "text": " - Landsman, Lawler, Katz (2020). Application of electrodialysis pretreatment to enhance boron \
                    removal and reduce fouling during nanofiltration/reverse osmosis",
            }
        ]
    },
}

empty_string_section_text = {
    "title": "Boron",
    "page_type": "compound",
    "metadata": [{"title": "contributors", "text": "Matt Landsman, Lauren Nalley"}],
    "documentation": {"sections": [{"title": "Internal publications", "text": ""}]},
}
