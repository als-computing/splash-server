from splash.resources.experiments import Experiments
import os
import tempfile

import pytest

from splash import app 

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db

@pytest.fixture
def client():
    
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(flaskr.app.config['DATABASE'])

@pytest.fixture
def app():
    app = create_app()
    return app