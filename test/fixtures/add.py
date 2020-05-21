import splash
import pytest
import mongomock


@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture
def splash_client(mongodb):
    app = splash.create_app(db=mongodb)
    app.config['TESTING'] = True
    return app.test_client()
