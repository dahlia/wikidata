import urllib.request

from pytest import fixture

from .mock import FixtureOpener
from wikidata.client import WIKIDATA_BASE_URL, Client
from wikidata.entity import Entity, EntityId


@fixture
def fx_client_opener() -> urllib.request.OpenerDirector:
    return FixtureOpener(WIKIDATA_BASE_URL)


@fixture
def fx_client(fx_client_opener: urllib.request.OpenerDirector) -> Client:
    return Client(opener=fx_client_opener)


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


@fixture
def fx_item(fx_loaded_entity: Entity) -> Entity:
    return fx_loaded_entity


@fixture
def fx_property(fx_client: Client) -> Entity:
    return fx_client.get(EntityId('P2003'))
