from pytest import fixture

from .mock import FixtureOpener
from wikidata.client import WIKIDATA_BASE_URL, Client
from wikidata.entity import Entity, EntityId


@fixture
def fx_client() -> Client:
    return Client(opener=FixtureOpener(WIKIDATA_BASE_URL))


@fixture(autouse=True)
def add_doctest_namespace(doctest_namespace,
                          fx_client: Client,
                          fx_loaded_entity: Entity):
    doctest_namespace['client'] = fx_client


@fixture
def fx_unloaded_entity(fx_client: Client) -> Entity:
    return fx_client.get(EntityId('Q1299'))


@fixture
def fx_loaded_entity(fx_client: Client) -> Entity:
    entity = fx_client.get(EntityId('Q494290'))
    entity.load()
    return entity
