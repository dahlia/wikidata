import pickle
import typing

from wikidata.cache import MemoryCachePolicy, ProxyCachePolicy


def test_memory_cache_policy():
    m = MemoryCachePolicy(max_size=5)
    assert m.get('a') is None
    m.set('a', 1)
    assert m.get('a') == 1
    m.set('b', 2)
    m.set('c', 3)
    m.set('d', 4)
    m.set('e', 5)
    m.set('f', 6)
    assert m.get('a') is None
    m.get('b')
    m.set('g', 7)
    assert m.get('b') == 2
    assert m.get('c') is None


class MockCache:

    def __init__(self) -> None:
        self.records = []  # type: typing.List[typing.Tuple[str, typing.List]]

    def get(self, key: str) -> typing.Optional[bytes]:
        self.records.append(('get', [key]))
        if key == 'wd/37b51d194a7513e45b56f6524f2d51f2':
            return pickle.dumps('cached value')
        return None

    def set(self, key: str, value: bytes, timeout: int = 0) -> None:
        self.records.append(('set', [key, value, timeout]))

    def delete(self, key: str) -> None:
        self.records.append(('delete', [key]))


def test_proxy_cache_policy():
    mock = MockCache()
    proxy = ProxyCachePolicy(mock, 123, 456, 'wd/')
    assert proxy.get('foo') is None
    assert len(mock.records) == 1
    assert mock.records[0] == ('get', ['wd/acbd18db4cc2f85cedef654fccc4a4d8'])
    assert proxy.get('bar') == 'cached value'
    assert len(mock.records) == 2
    assert mock.records[1] == ('get', ['wd/37b51d194a7513e45b56f6524f2d51f2'])
    proxy.set('baz', 'asdf')
    assert len(mock.records) == 3
    assert mock.records[2][0] == 'set'
    assert mock.records[2][1][0] == 'wd/73feffa4b7f6bb68e44cf984c85f6e88'
    assert pickle.loads(mock.records[2][1][1]) == 'asdf'
    assert mock.records[2][1][2] == 123
    proxy.set('qux', None)
    assert len(mock.records) == 4
    assert (mock.records[3] ==
            ('delete', ['wd/d85b1213473c2fd7c2045020a6b9c62b']))
    proxy.set('https://www.wikidata.org/wiki/Special:EntityData/P18.json',
              'foo')
    assert len(mock.records) == 5
    assert mock.records[4][0] == 'set'
    assert mock.records[4][1][0] == 'wd/a071db2de830f9369edfcb773750ccc9'
    assert pickle.loads(mock.records[4][1][1]) == 'foo'
    assert mock.records[4][1][2] == 456
