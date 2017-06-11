from wikidata.cache import MemoryCachePolicy


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
