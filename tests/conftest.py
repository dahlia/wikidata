import urllib.request
from typing import AbstractSet, FrozenSet, Optional, Sequence, Set, Union, cast

from pytest import fixture

from wikidata.client import Client, WIKIDATA_BASE_URL
from wikidata.commonsmedia import File
from wikidata.entity import Entity, EntityId

from .mock import FixtureOpener


def pytest_assertrepr_compare(op: str, left, right) -> Optional[Sequence[str]]:
    # set of entities
    if op == '==' and isinstance(left, (set, frozenset)) and \
       isinstance(right, (set, frozenset)) and \
       all(isinstance(v, Entity) for v in left) and \
       all(isinstance(v, Entity) for v in right):
        def repr_ids(ids: AbstractSet[EntityId]) -> str:
            sorted_ids = sorted(
                ids,
                key=lambda i: (
                    i[0],
                    # Since EntityIds usually consist of one letter followed
                    # by digits, order them numerically.  If it's not in
                    # that format they should be sorted in the other bucket.
                    (0, int(i[1:])) if i[1:].isdigit() else (1, i[1:])
                )
            )
            return '{' + ', '.join(sorted_ids) + '}'
        left = cast(Union[Set[Entity], FrozenSet[Entity]], left)
        right = cast(Union[Set[Entity], FrozenSet[Entity]], right)
        left_ids = {e.id for e in left}
        right_ids = {e.id for e in right}
        return [
            '{} == {}'.format(repr_ids(left_ids), repr_ids(right_ids)),
            'Extra entities in the left set:',
            repr_ids(left_ids - right_ids),
            'Extra entities in the right set:',
            repr_ids(right_ids - left_ids),
        ]
    return None


@fixture
def fx_client_opener() -> urllib.request.OpenerDirector:
    return FixtureOpener(WIKIDATA_BASE_URL)


@fixture
def fx_client(fx_client_opener: urllib.request.OpenerDirector) -> Client:
    return Client(opener=fx_client_opener)


@fixture(autouse=True)
def add_doctest_namespace(doctest_namespace, fx_client: Client):
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
def fx_redirected_entity(fx_client: Client) -> Entity:
    return fx_client.get(EntityId('Q16231742'))


@fixture
def fx_item(fx_loaded_entity: Entity) -> Entity:
    return fx_loaded_entity


@fixture
def fx_property(fx_client: Client) -> Entity:
    return fx_client.get(EntityId('P2003'))


@fixture
def fx_file(fx_client: Client) -> File:
    return File(fx_client, 'File:Gandhara Buddha (tnm).jpeg')
