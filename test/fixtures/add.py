import splash
import pytest
import mongomock


@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture
def splash_client(mongodb):
    app = splash.create_app()
    app.config['TESTING'] = True
    app.db = mongodb
    return app.test_client()
