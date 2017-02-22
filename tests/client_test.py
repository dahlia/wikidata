import urllib.request

from wikidata.client import Client
from wikidata.entity import Entity, EntityId, EntityType


def test_client_get(fx_client: Client):
    entity = fx_client.get(EntityId('Q1299'))
    assert isinstance(entity, Entity)
    assert entity.data is None
    assert entity.id == EntityId('Q1299')
    entity2 = fx_client.get(EntityId('Q1299'), load=True)
    assert entity2.data is not None
    assert entity2 is entity


def test_client_guess_entity_type(
    fx_client_opener: urllib.request.OpenerDirector
):
    guess_client = Client(opener=fx_client_opener, entity_type_guess=True)
    assert guess_client.guess_entity_type(EntityId('Q1299')) is EntityType.item
    assert (guess_client.guess_entity_type(EntityId('P434')) is
            EntityType.property)
    assert guess_client.guess_entity_type(EntityId('NotApplicable')) is None
    noguess_client = Client(opener=fx_client_opener, entity_type_guess=False)
    assert noguess_client.guess_entity_type(EntityId('Q1299')) is None
    assert noguess_client.guess_entity_type(EntityId('P434')) is None
    assert noguess_client.guess_entity_type(EntityId('NotApplicable')) is None


def test_client_request(fx_client: Client):
    data = fx_client.request('./wiki/Special:EntityData/Q1299.json')
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
        "wikidata.client.Client('https://www.wikidata.org/')"
