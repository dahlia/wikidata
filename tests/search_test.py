import pytest
from unittest.mock import Mock, patch

from wikidata.search import (
    SearchResult,
    _search,
    _SearchResultParser,
    _calculate_similarity,
    filter_by_similarity,
    suggest_query,
)
from wikidata.entity import EntityId


# Tests for the similarity calculation function
def test_calculate_similarity_exact_match():
    """Test similarity score for exact match."""
    score = _calculate_similarity('Haiti', 'Haiti')
    assert score == 100.0


def test_calculate_similarity_partial_match():
    """Test similarity score for partial match."""
    score = _calculate_similarity('Haiti', 'Haitian Creole')
    assert 50 <= score < 100


# Tests for the HTML parser
def test_parser_initialization():
    """Test parser initialization."""
    parser = _SearchResultParser()
    assert parser.results == []
    assert parser.in_search_result is False


def test_parse_single_result():
    """Test parsing a single search result from HTML."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
        <span class="wb-itemlink-description">country in the Caribbean Sea</span>
    </li>
    '''
    parser = _SearchResultParser()
    parser.feed(html)
    
    assert len(parser.results) == 1
    assert parser.results[0].entity_id == 'Q790'
    assert parser.results[0].name == 'Haiti'
    assert parser.results[0].description == 'country in the Caribbean Sea'


def test_parse_multiple_results():
    """Test parsing multiple search results."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haitian Creole</span>
            <span class="wb-itemlink-id">(Q33491)</span>
        </div>
    </li>
    '''
    parser = _SearchResultParser()
    parser.feed(html)
    
    assert len(parser.results) == 2
    assert parser.results[0].entity_id == 'Q790'
    assert parser.results[0].name == 'Haiti'


# Tests for the main search function
@patch('wikidata.search.urllib.request.urlopen')
def test_search_basic(mock_urlopen):
    """Test basic search functionality."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
    </li>
    '''
    mock_response = Mock()
    mock_response.read.return_value = html.encode('utf-8')
    mock_urlopen.return_value = mock_response

    results = _search('Haiti', limit=10)
    
    assert len(results) == 1
    assert results[0].entity_id == 'Q790'
    assert results[0].name == 'Haiti'
    assert results[0].similarity_score == 100.0


@patch('wikidata.search.urllib.request.urlopen')
def test_search_with_limit(mock_urlopen):
    """Test search result limiting."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haitian Creole</span>
            <span class="wb-itemlink-id">(Q33491)</span>
        </div>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Port-au-Prince</span>
            <span class="wb-itemlink-id">(Q34261)</span>
        </div>
    </li>
    '''
    mock_response = Mock()
    mock_response.read.return_value = html.encode('utf-8')
    mock_urlopen.return_value = mock_response

    results = _search('Haiti', limit=2, likeness_threshold=0.5)
    
    assert len(results) == 2


@patch('wikidata.search.urllib.request.urlopen')
def test_search_sorts_by_similarity(mock_urlopen):
    """Test that results are sorted by similarity score."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Japan</span>
            <span class="wb-itemlink-id">(Q17)</span>
        </div>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
    </li>
    '''
    mock_response = Mock()
    mock_response.read.return_value = html.encode('utf-8')
    mock_urlopen.return_value = mock_response

    results = _search('Haiti', limit=10, likeness_threshold=0.2)
    
    # Haiti should have higher similarity than Japan
    assert len(results) >= 2
    assert results[0].name == 'Haiti'
    assert results[0].similarity_score > results[1].similarity_score


@patch('wikidata.search.urllib.request.urlopen')
def test_search_empty_results(mock_urlopen):
    """Test search with no results."""
    mock_response = Mock()
    mock_response.read.return_value = b'<div></div>'
    mock_urlopen.return_value = mock_response

    results = _search('XYZ_NONEXISTENT_ENTITY_12345', limit=10)
    
    assert len(results) == 0


@patch('wikidata.search.urllib.request.urlopen')
def test_search_with_likeness_threshold(mock_urlopen):
    """Test search with likeness threshold filtering."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Japan</span>
            <span class="wb-itemlink-id">(Q17)</span>
        </div>
    </li>
    '''
    mock_response = Mock()
    mock_response.read.return_value = html.encode('utf-8')
    mock_urlopen.return_value = mock_response

    # With threshold of 1.0 (100%), only exact matches
    results = _search('Haiti', limit=10, likeness_threshold=1.0)
    assert len(results) == 1
    assert results[0].name == 'Haiti'

    # With threshold of 0.0, include all results
    results = _search('Haiti', limit=10, likeness_threshold=0.0)
    assert len(results) == 2


@patch('wikidata.search.urllib.request.urlopen')
def test_search_with_entity_type_filter(mock_urlopen):
    """Test search with entity type filtering."""
    html = '''
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haiti</span>
            <span class="wb-itemlink-id">(Q790)</span>
        </div>
        <span class="wb-itemlink-description">country in the Caribbean</span>
    </li>
    <li class="mw-search-result mw-search-result-ns-0">
        <div class="mw-search-result-heading">
            <span class="wb-itemlink-label">Haitian Creole</span>
            <span class="wb-itemlink-id">(Q33491)</span>
        </div>
        <span class="wb-itemlink-description">language spoken in Haiti</span>
    </li>
    '''
    mock_response = Mock()
    mock_response.read.return_value = html.encode('utf-8')
    mock_urlopen.return_value = mock_response

    # Filter for 'country' type
    results = _search('Haiti', limit=10, entity_type='country', likeness_threshold=0.5)
    assert len(results) == 1
    assert results[0].entity_id == 'Q790'

    # Filter for 'language' type
    results = _search('Haiti', limit=10, entity_type='language', likeness_threshold=0.5)
    assert len(results) == 1
    assert results[0].entity_id == 'Q33491'


def test_filter_by_similarity():
    """Test filtering search results by similarity score."""
    results = [
        SearchResult(EntityId('Q1'), 'Entity One', 100.0, 'description'),
        SearchResult(EntityId('Q2'), 'Entity Two', 75.0, 'description'),
        SearchResult(EntityId('Q3'), 'Entity Three', 50.0, 'description'),
        SearchResult(EntityId('Q4'), 'Entity Four', 25.0, 'description'),
    ]
    
    # Filter for 80% or higher
    filtered = filter_by_similarity(results, 80.0)
    assert len(filtered) == 1
    assert filtered[0].entity_id == 'Q1'
    
    # Filter for 50% or higher
    filtered = filter_by_similarity(results, 50.0)
    assert len(filtered) == 3
    assert filtered[0].entity_id == 'Q1'
    assert filtered[2].entity_id == 'Q3'

# Tests for the suggest_query function
@patch('wikidata.search._search')
def test_suggest_query_basic(mock_search):
    """Test basic query suggestion."""
    mock_search.return_value = [
        SearchResult(EntityId('Q790'), 'Haiti', 95.0, 'country'),
        SearchResult(EntityId('Q33491'), 'Haitian Creole', 85.0, 'language'),
    ]
    
    suggestions = suggest_query('hati', max_suggestions=5)
    assert len(suggestions) > 0
    assert any('Haiti' in s for s in suggestions)


@patch('wikidata.search._search')
def test_suggest_query_no_results(mock_search):
    """Test suggestion when no search results found."""
    mock_search.return_value = []
    suggestions = suggest_query('xyz_nonexistent_12345', max_suggestions=5)
    assert len(suggestions) == 0