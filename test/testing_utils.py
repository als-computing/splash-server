import json
from flask import current_app
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers

def generic_test_flask_crud(sample_new_object, url_path, client, mongodb):
    user = {"uid": "foo_uid"}
    
    with client.application.app_context() as app_context:
        access_token = create_access_token(identity="dfdfgdfgdfg")
        # headers = Headers()
        # headers.add_header("Authorization", "Bearer " + access_token)  
        
        with client.application.test_request_context(url_path) as request_context:
                client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + access_token
                response = client.post(url_path,
                                data=json.dumps(sample_new_object),
                                content_type='application/json')
                request = request_context.request
                print("!!!!!!!!!" + repr(response))
                assert response.status_code == 200

    
                response_dict = json.loads(response.get_json())
                new_uid = response_dict['uid']
                assert new_uid

                # retreive all
                response = client.get(url_path)
                assert response.status_code == 200
                response_dict = response.get_json()
                assert response_dict['total_results'] == 1

                # retrive one
                response = client.get(url_path + '/' + new_uid)
                assert response.status_code == 200
                sample_new_object_returned = response.get_json()
                sample_new_object_returned.pop('_id', None)  # comparing dicts will fail with mongo's _id
                sample_new_object['uid'] = sample_new_object_returned['uid']  # now let's give the generated uid so we can compare
                assert sample_new_object_returned == sample_new_object
