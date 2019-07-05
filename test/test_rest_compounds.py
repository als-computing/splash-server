import pytest
import pytest_flask
import pytest_mongodb
from flask import Response
import splash.server

compounds = [  {
    "name": "Boron",
    "document": True,
    "produced_water_relevance": "Toxicity",
    "mwet_relevance": "Presence in geologic formations",
    "challenges": "Uncharged at neutral pH",
    "aqueous_props": "Boric acid (pKa=9.3)",
    "adsorption_props": "Chelating resins",
    "analytical_techniques": "ICP",
    "spectroscopic_techniques": "XAS",
    "created_by": {"name": "Matt Landsman", "email": "mrlandsman@utexas.edu"}
  }]

class CompoundsResponse(Response):

    @property
    def json(self):
        return compounds

# @pytest.fixture
# def app(mongodb):
#
#     app = splash.server.create_app(mongodb)
#     app.db = mongodb
#     app.response_class = CompoundsResponse
#     return app

def test_get_compounds(client):

    response = client.get(splash.server.COMPOUNDS_URL_ROOT)
    assert response == []
