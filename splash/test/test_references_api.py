import pytest
import json


# TODO: Test that the time of the documents is correct, test that the user uid is correct
# Test the put functions
@pytest.mark.usefixtures("splash_client", "token_header")
def test_flask_crud_user(api_url_root, splash_client, token_header):
    url_path = api_url_root + "/references"
    response = splash_client.post(url_path,
                                  data='{',
                                  headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    reference_1['uid'] = 'test'
    response = splash_client.post(url_path,
                                  data=json.dumps(reference_1),
                                  headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    # response = splash_client.put(url_path + "/sample_uid",
    #                              data=json.dumps(reference_1),
    #                              headers=token_header)
    # assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    reference_1.pop('uid')
    response = splash_client.post(url_path,
                                  data=json.dumps(reference_1),
                                  headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    response_dict = response.json()
    new_uid = response_dict['uid']
    assert new_uid

    # retreive all
    response = splash_client.get(url_path, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    response_dict = response.json()
    assert len(response_dict) > 0

    # retrive one
    response = splash_client.get(url_path + '/uid/' + new_uid, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    response = splash_client.get(url_path + '/doi/' + reference_1['DOI'], headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"


def test_search(api_url_root, splash_client, token_header):
    url = api_url_root + "/references"

    response = splash_client.post(url,
                                  data=json.dumps(reference_2),
                                  headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    response = splash_client.get(url+"?search=Middle", headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 2
    assert any(reference_1["title"] == page["title"] for page in resp_obj)
    assert any(reference_2["title"] == page["title"] for page in resp_obj)

    response = splash_client.get(url+"?search=Gandalf", headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 2
    assert any(reference_1["title"] == page["title"] for page in resp_obj)
    assert any(reference_2["title"] == page["title"] for page in resp_obj)

    response = splash_client.get(url+"?search=Wizards", headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 1
    assert resp_obj[0]['title'] == reference_2['title']

    response = splash_client.get(url+"?search=ecological", headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    resp_obj = response.json()
    assert len(resp_obj) == 1
    assert resp_obj[0]['title'] == reference_1['title']


reference_1 = {
    "DOI": "10.5406/jfilmvideo.67.3-4.0079",
    "title": "The ecological relationship between Mordor and Middle Earth: A life systems analysis",
    "author": [{"family": "The Grey", "given": "Gandalf"}, {"family": "The White", "given": "Saruman"}],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}

reference_2 = {
    "DOI": "10.5406/mordor",
    "title": "The Effects of Sauron's Ring on Middle Earth: A meta-analysis.",
    "author": [{"family": "The Grey", "given": "Gandalf"}, {"literal": "Wizards Inc."}],
    "origin_url": "https://data.crossref.org/10.5406/jfilmvideo.67.3-4.0079",
}
