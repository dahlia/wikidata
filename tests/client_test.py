from wikidata.client import Client
from wikidata.entity import Entity, EntityId


def test_client_get(fx_client: Client):
    entity = fx_client.get(EntityId('Q1299'))
    assert isinstance(entity, Entity)
    assert entity.data is None
    assert entity.id == EntityId('Q1299')


def test_client_request(fx_client: Client):
    data = fx_client.request(EntityId('Q1299'))
    assert isinstance(data, dict)
    assert set(data) == {'entities'}
    entities = data['entities']
    assert isinstance(entities, dict)
    assert set(entities) == {'Q1299'}
    entity = entities['Q1299']
    assert isinstance(entity, dict)
    assert set(entity) >= {
        'pageid', 'ns', 'title', 'lastrevid', 'modified', 'type', 'id',
        'labels', 'descriptions', 'aliases', 'claims', 'sitelinks'
    }
    assert entity['title'] == 'Q1299'
    assert entity['type'] == 'item'
    assert entity['labels']['en'] == {'language': 'en', 'value': 'The Beatles'}


def test_client_repr():
    assert repr(Client(repr_string='repr_string test')) == 'repr_string test'
    assert repr(Client()) == \
        "wikidata.client.Client('https://www.wikidata.org/wiki/')"
