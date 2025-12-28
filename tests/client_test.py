import json
import pickle
import urllib.request
from typing import Optional, TYPE_CHECKING
from unittest.mock import patch

from wikidata.cache import CacheKey, CachePolicy, CacheValue
from wikidata.client import Client
from wikidata.entity import Entity, EntityId, EntityState, EntityType
from wikidata.multilingual import Locale
from wikidata.search import SearchResult

from .mock import FixtureOpener

if TYPE_CHECKING:
    from typing import Dict, Union  # noqa: F401


def test_client_get(fx_client: Client):
    entity = fx_client.get(EntityId('Q1299'))
    assert isinstance(entity, Entity)
    assert entity.data is None
    assert entity.id == EntityId('Q1299')
    entity2 = fx_client.get(EntityId('Q1299'), load=True)
    assert entity2.data is not None
    assert entity2 is entity
    entity3 = fx_client.get(EntityId('1299'), load=True)  # http 400 error
    assert entity3.state is EntityState.non_existent


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


@patch('wikidata.client._search')
def test_client_search(mock_search):
    # Test case 1: Multiple results with different similarity scores
    mock_results = [
        SearchResult(
            entity_id=EntityId('Q790'),
            name='Haiti',
            similarity_score=100.0,
            description='Country in the Caribbean'
        ),
        SearchResult(
            entity_id=EntityId('Q33281'),
            name='Haitian Creole',
            similarity_score=75.0,
            description='Language spoken in Haiti'
        ),
    ]
    mock_search.return_value = mock_results
    
    client = Client()
    results = client.search('Haiti')
    
    assert len(results) == 2
    assert results[0].entity_id == EntityId('Q790')
    assert results[0].name == 'Haiti'
    assert results[0].similarity_score == 100.0
    assert results[1].entity_id == EntityId('Q33281')
    assert results[1].similarity_score == 75.0
    mock_search.assert_called_once()
    
    # Test case 2: Empty results
    mock_search.reset_mock()
    mock_search.return_value = []
    results_empty = client.search('NonexistentXYZ')
    assert len(results_empty) == 0
    
    # Test case 3: Single result
    mock_search.reset_mock()
    single_result = [
        SearchResult(
            entity_id=EntityId('Q42'),
            name='Answer',
            similarity_score=85.5,
            description='The answer'
        ),
    ]
    mock_search.return_value = single_result
    results_single = client.search('Answer')
    assert len(results_single) == 1
    assert results_single[0].entity_id == EntityId('Q42')
    assert results_single[0].similarity_score == 85.5
    
    # Test case 4: With parameters
    mock_search.reset_mock()
    results_with_params = client.search(
        'test',
        limit=5,
        language='en',
        entity_type='person',
        likeness_threshold=0.8
    )
    mock_search.assert_called_once()

class MockCachePolicy(CachePolicy):

    def __init__(self) -> None:
        self.store = {
        }  # type: Dict[Union[CacheKey, str], Optional[CacheValue]]

    def get(self, key: CacheKey) -> Optional[CacheValue]:
        return self.store.get(key)

    def set(self, key: CacheKey, value: Optional[CacheValue]) -> None:
        self.store[key] = value


def test_client_cache_policy(fx_client_opener: FixtureOpener):
    mock = MockCachePolicy()
    client1 = Client(opener=fx_client_opener, cache_policy=mock)
    e1 = client1.get(EntityId('Q1299'), load=True)
    assert len(fx_client_opener.records) == 1
    url = 'https://www.wikidata.org/wiki/Special:EntityData/Q1299.json'
    url_open = fx_client_opener.open
    assert frozenset(mock.store) == {url}
    assert mock.store[url] == json.loads(url_open(url).read().decode('utf-8'))
    assert len(fx_client_opener.records) == 2
    client2 = Client(opener=fx_client_opener, cache_policy=mock)
    e2 = client2.get(EntityId('Q1299'), load=True)
    assert e1.attributes == e2.attributes
    assert len(fx_client_opener.records) == 2


def test_client_pickle(fx_client: Client):
    dumped = pickle.dumps(fx_client)
    c = pickle.loads(dumped)
    entity = c.get(EntityId('Q1299'), load=True)
    assert isinstance(entity, Entity)
    assert entity.label[Locale('en')] == 'The Beatles'


def test_client_repr():
    assert repr(Client(repr_string='repr_string test')) == 'repr_string test'
    assert repr(Client()) == \
        "wikidata.client.Client('https://www.wikidata.org/')"