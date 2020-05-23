import json
from flask import current_app
from flask_login import login_user, current_user
from splash.login import User


def generic_test_flask_crud(sample_new_object, url_path, client, mongodb):
    user = User("foo_uid", "foo_email", "foo", "bar", True)
    with client.application.app_context() as app_context:
        
        @app_context.app.login_manager.request_loader
        def loader(request):
            return user
       
        with client.application.test_request_context(url_path):
                login_user(user, remember=True)

                response = client.post(url_path,
                                data=json.dumps(sample_new_object),
                                content_type='application/json')
                assert response.status_code == 200

    
    response_dict = json.loads(response.get_json())
    new_uid = response_dict['uid']
    assert new_uid

    # retreive all
    response = client.get(url_path)
    assert response.status_code == 200
    response_dict = json.loads(response.get_json())
    assert response_dict['total_results'] == 1

    # retrive one
    response = client.get(url_path + '/' + new_uid)
    assert response.status_code == 200
    sample_new_object_returned = json.loads(response.get_json())
    sample_new_object_returned.pop('_id', None)  # comparing dicts will fail with mongo's _id
    sample_new_object['uid'] = sample_new_object_returned['uid']  # now let's give the generated uid so we can compare
    assert sample_new_object_returned == sample_new_object
