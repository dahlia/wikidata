from pytest import fixture

from wikidata.client import Client
from wikidata.entity import Entity, EntityId
from wikidata.globecoordinate import GlobeCoordinate


@fixture
def fx_globecoordinate() -> GlobeCoordinate:
    client = Client()
    return GlobeCoordinate(
        latitude=70.1525,
        longitude=70.1525,
        precision=0.0002777777777777778,
        globe=client.get(EntityId("Q111")))


def test_globecoordinate_value(fx_globecoordinate: GlobeCoordinate):
    assert fx_globecoordinate.latitude == 70.1525
    assert fx_globecoordinate.longitude == 70.1525
    assert fx_globecoordinate.precision == 0.0002777777777777778
    assert isinstance(fx_globecoordinate.globe, Entity)
    assert fx_globecoordinate.globe.id == "Q111"


def test_globecoordinate_repr(fx_globecoordinate: GlobeCoordinate):
    assert (repr(fx_globecoordinate) ==
            ("wikidata.globecoordinate.GlobeCoordinate(70.1525, 70.1525, "
             "<wikidata.entity.Entity Q111>, 0.0002777777777777778)"))
