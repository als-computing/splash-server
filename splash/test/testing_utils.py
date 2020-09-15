import json
import pytest


@pytest.mark.usefixtures("splash_client")
def generic_test_api_crud(sample_new_object, url_path, splash_client, token_header):
    response = splash_client.post(url_path,
                                  data='{',
                                  headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    sample_new_object['uid'] = 'test'
    response = splash_client.post(url_path,
                                  data=json.dumps(sample_new_object),
                                  headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    response = splash_client.put(url_path + "/sample_uid",
                                 data=json.dumps(sample_new_object),
                                 headers=token_header)
    assert response.status_code == 422, f"{response.status_code}: response is {response.content}"

    sample_new_object.pop('uid')
    response = splash_client.post(url_path,
                                  data=json.dumps(sample_new_object),
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
    response = splash_client.get(url_path + '/' + new_uid, headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    response = splash_client.put(url_path + '/' + new_uid, data=json.dumps(sample_new_object), headers=token_header)
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"

    # we used to validate more, but with the switch tn FastAPI, new object models aren't the same
    # as existing object models
    # sample_new_object_returned = response.json()
    # sample_new_object['uid'] = sample_new_object_returned['uid']  # now let's give the generated uid so we can compare
    # assert sample_new_object_returned == sample_new_object
