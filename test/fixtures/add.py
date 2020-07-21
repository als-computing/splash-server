import pytest
import mongomock


class PrimaryStream():
    metadata = {'descriptors': []}

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture
def splash_client(mongodb, monkeypatch, ):
    monkeypatch.setenv('FLASK_SECRET_KEY', "the_question_to_the_life_the_universe_and_everything")
    # This ensures that we can appropriately mock
    import splash
    app = splash.create_app(db=mongodb)
    app.config['TESTING'] = True
    return app.test_client()
