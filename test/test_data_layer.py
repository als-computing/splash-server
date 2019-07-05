import pytest
import mongomock

from splash.data import MongoCollectionDao

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db

def test_crud_compounds(mongodb):
    mongo_crud_service = MongoCollectionDao(mongodb.compounds)
    compound = dict(name='boron')
    id = mongo_crud_service.create(compound)
    assert id is not None
    retrieved_compound = mongo_crud_service.retrieve(id)
    assert retrieved_compound['_id'] == id
    assert retrieved_compound['name'] == 'boron'

    #test update
    compound['name'] = 'dilithium crystals'
    mongo_crud_service.update(compound)
    retrieved_compound = mongo_crud_service.retrieve(id)
    assert retrieved_compound['name'] == 'dilithium crystals'

    #test delete
    mongo_crud_service.delete(retrieved_compound['_id'])
    assert mongo_crud_service.retrieve(id) is None

