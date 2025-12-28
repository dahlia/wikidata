import html.parser
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher, get_close_matches
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
    from urllib.request import OpenerDirector
else:
    WIKIDATA_BASE_URL = 'https://www.wikidata.org/'
    
from .entity import EntityId

__all__ = ['SearchResult', 'suggest_query', 'filter_by_similarity']


@dataclass 
class SearchResult:
    """Represents a single search result from Wikidata.
    
    :param entity_id: The Wikidata entity ID (e.g., 'Q790')
    :type entity_id: :class:`EntityId`
    :param name: The official name of the entity
    :type name: :class:`str`
    :param similarity_score: The similarity score between the search query and the result name
                           as a percentage (0-100)
    :type similarity_score: :class:`float`
    :param description: Optional description of the entity
    :type description: :class:`str` or :const:`None`
    """
    entity_id: EntityId
    name: str
    similarity_score: float
    description: Optional[str] = None

    def __repr__(self) -> str:
        return (
            f'SearchResult(entity_id={self.entity_id!r}, name={self.name!r}, '
            f'similarity_score={self.similarity_score:.1f}%, '
            f'description={self.description!r})'
        )

def _search(
    query: str,
    limit: int = 10,
    opener: Optional['OpenerDirector'] = None,
    client: Optional['Client'] = None,
    language: Optional[str] = None,
    entity_type: Optional[str] = None,
    likeness_threshold: float = 1.0,
    verbose: bool = False,
) -> List[SearchResult]:
    """
    Search Wikidata for entities by name or search term.
    
    This function performs a full-text search on Wikidata and returns a list of 
    matching entities with their IDs and similarity scores. Results are sorted by
    similarity score in descending order.
    
    :param query: The search term (entity name or part of it)
    :type query: :class:`str`
    :param limit: Maximum number of results to return (default: 10)
    :type limit: :class:`int`
    :param opener: Optional urllib OpenerDirector for custom HTTP handling. Ignored if client is provided
    :type opener: :class:`urllib.request.OpenerDirector`
    :param client: Optional Client instance to use for HTTP requests. If provided,
                   the client's base URL will be used instead of the default Wikidata URL
    :type client: :class:`Client`
    :param language: Optional language code (e.g., 'en', 'fr', 'es') to search using
                     labels/descriptions in that language (default: None, uses English)
    :type language: :class:`str`
    :param entity_type: Optional filter for entity type. Can be 'person', 'place', 'organization',
                        'work', etc. Filters results based on description content
    :type entity_type: :class:`str`
    :param likeness_threshold: Minimum similarity score threshold (0-1) for results to include.
                              For example, 0.6 means only return results with 60% or higher similarity
                              (default: 1.0, returns only exact matches)
    :type likeness_threshold: :class:`float`
    :param verbose: If True, pretty print the search results to stdout (default: False)
    :type verbose: :class:`bool`
    :return: A list of SearchResult objects sorted by similarity score (highest first),
             filtered by likeness_threshold if provided
    :rtype: :class:`List`\\ [:class:`SearchResult`]
    :raises urllib.error.URLError: If the HTTP request fails
    
    """
    # Validate input
    if not query or not isinstance(query, str):
        return []

    if limit < 1:
        limit = 1
    
    # Validate likeness_threshold
    if not 0.0 <= likeness_threshold <= 1.0:
        likeness_threshold = 1.0

    # Determine which base_url and opener to use
    if client is not None:
        search_base_url = client.base_url
        http_opener = client.opener
    else:
        search_base_url = WIKIDATA_BASE_URL
        http_opener = opener

    # Build search URL
    search_url = f'{search_base_url}w/index.php?search={urllib.parse.quote(query)}'
    
    # Add language parameter if specified
    if language:
        search_url += f'&language={urllib.parse.quote(language)}'

    try:
        # Fetch the search results page
        req = urllib.request.Request(search_url)

        # Add User-Agent header to avoid 403 Forbidden responses
        user_agent = (
            'WikidataClientPython '
            '(https://github.com/dahlia/wikidata; hong@minhee.org)'
        )
        req.add_header('User-Agent', user_agent)

        if http_opener is None:
            response = urllib.request.urlopen(req)
        else:
            response = http_opener.open(req)

        html_content = response.read().decode('utf-8')

    except urllib.error.URLError as e:
        raise

    # Parse HTML and extract results
    parser = _SearchResultParser()
    parser.feed(html_content)

    # Calculate similarity scores
    for result in parser.results:
        result.similarity_score = _calculate_similarity(query, result.name)

    # Sort by similarity score (highest first)
    sorted_results = sorted(
        parser.results,
        key=lambda r: r.similarity_score,
        reverse=True
    )

    # Filter by entity type if specified
    if entity_type:
        sorted_results = [
            result for result in sorted_results
            if result.description and entity_type.lower() in result.description.lower()
        ]
    
    # Filter by likeness threshold
    if likeness_threshold > 0.0:
        min_similarity = likeness_threshold * 100
        sorted_results = filter_by_similarity(sorted_results, min_similarity)
    
    # Return top N results
    final_results = sorted_results[:limit]

    # Pretty print results if verbose mode is enabled
    if verbose and final_results:
        print(f"\n{'='*80}")
        print(f"Search Results for '{query}'")
        print(f"Limit: {limit} | Likeness Threshold: {likeness_threshold*100:.1f}%")
        print(f"{'='*80}\n")
        for i, result in enumerate(final_results, 1):
            print(f"{i}. {result.name}")
            print(f"   Entity ID: {result.entity_id}")
            print(f"   Similarity: {result.similarity_score:.1f}%")
            if result.description:
                print(f"   Description: {result.description}")
            print()

    return final_results

def filter_by_similarity(results: List[SearchResult], min_similarity: float) -> List[SearchResult]:
    """
    Filter search results by minimum similarity score.
    
    :param results: List of SearchResult objects to filter
    :type results: :class:`List`\\ [:class:`SearchResult`]
    :param min_similarity: Minimum similarity threshold (0-100)
    :type min_similarity: :class:`float`W
    :return: New list with filtered results
    :rtype: :class:`List`\\ [:class:`SearchResult`]
    
    """
    filtered = [
        result for result in results
        if result.similarity_score >= min_similarity
    ]
    return filtered


class _SearchResultParser(html.parser.HTMLParser):
    """HTML parser for extracting search results from Wikidata search pages."""

    def __init__(self) -> None:
        super().__init__()
        self.results: List[SearchResult] = []
        self.in_search_result = False
        self.in_result_heading = False
        self.in_itemlink_label = False
        self.in_itemlink_id = False
        self.in_description = False
        self.in_searchmatch = False
        self.current_entity_id: Optional[str] = None
        self.current_name: Optional[str] = None
        self.current_description: Optional[str] = None
        self.name_buffer = []
        self.id_buffer = []
        self.description_buffer = []

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        """Process opening HTML tags.
        
        :param tag: The HTML tag name
        :type tag: :class:`str`
        :param attrs: List of HTML attributes as (name, value) tuples
        :type attrs: :class:`List`\\ [:class:`tuple`]
        :return: None
        :rtype: :const:`None`
        """
        attr_dict = dict(attrs)
        
        # Check if we're entering a search result block
        if tag == 'li' and 'class' in attr_dict:
            if 'mw-search-result' in attr_dict['class'] and 'mw-search-result-ns-0' in attr_dict['class']:
                self.in_search_result = True

        # Check for result heading
        elif tag == 'div' and self.in_search_result and 'class' in attr_dict:
            if 'mw-search-result-heading' in attr_dict['class']:
                self.in_result_heading = True

        # Check for itemlink label (entity name)
        elif tag == 'span' and 'class' in attr_dict:
            if 'wb-itemlink-label' in attr_dict['class'] and self.in_result_heading:
                self.in_itemlink_label = True
            elif 'wb-itemlink-id' in attr_dict['class'] and self.in_result_heading:
                self.in_itemlink_id = True
            elif 'wb-itemlink-description' in attr_dict['class'] and self.in_search_result:
                self.in_description = True
            elif 'searchmatch' in attr_dict['class']:
                self.in_searchmatch = True

    def handle_endtag(self, tag: str) -> None:
        """Process closing HTML tags.
        
        :param tag: The HTML tag name
        :type tag: :class:`str`
        :return: None
        :rtype: :const:`None`
        """
        # Finalize search result when closing </li> tag
        if tag == 'li' and self.in_search_result:
            self.in_search_result = False
            self._finalize_result()

        # Closing result heading
        elif tag == 'div' and self.in_result_heading:
            self.in_result_heading = False

        # Closing span tags
        elif tag == 'span':
            if self.in_searchmatch:
                self.in_searchmatch = False
            elif self.in_itemlink_label:
                self.in_itemlink_label = False
            elif self.in_itemlink_id:
                self.in_itemlink_id = False
            elif self.in_description:
                self.in_description = False

    def handle_data(self, data: str) -> None:
        """Process text data within HTML tags.
        
        :param data: The text data to process
        :type data: :class:`str`
        :return: None
        :rtype: :const:`None`
        """
        # Append data to appropriate buffer based on current context
        if self.in_itemlink_label:
            self.name_buffer.append(data)
        elif self.in_itemlink_id:
            self.id_buffer.append(data)
        elif self.in_description:
            self.description_buffer.append(data)

    def handle_entityref(self, name: str) -> None:
        """Handle HTML entity references (e.g., &#039; for apostrophe).
        
        :param name: The name of the HTML entity (without & and ;)
        :type name: :class:`str`
        :return: None
        :rtype: :const:`None`
        """
        # Append the unescaped entity to the appropriate buffer
        if self.in_itemlink_label:
            self.name_buffer.append(html.unescape(f'&{name};'))
        elif self.in_itemlink_id:
            self.id_buffer.append(html.unescape(f'&{name};'))
        elif self.in_description:
            self.description_buffer.append(html.unescape(f'&{name};'))

    def handle_charref(self, name: str) -> None:
        """Handle numeric character references (e.g., &#39; for apostrophe).
        
        :param name: The numeric character reference (without & and ;)
        :type name: :class:`str`
        :return: None
        :rtype: :const:`None`
        """
        # Convert numeric reference to character and append to buffer
        if self.in_itemlink_label:
            self.name_buffer.append(chr(int(name)))
        elif self.in_itemlink_id:
            self.id_buffer.append(chr(int(name)))
        elif self.in_description:
            self.description_buffer.append(chr(int(name)))

    def _finalize_result(self) -> None:
        """Finalize and add the current search result to the results list.
        
        :return: None
        :rtype: :const:`None`
        """
        name = ''.join(self.name_buffer).strip()
        id_text = ''.join(self.id_buffer).strip()
        description = ''.join(self.description_buffer).strip()

        # Extract entity ID from parentheses (e.g., "(Q790)" -> "Q790")
        entity_id_match = re.search(r'\(([QP]\d+)\)', id_text)
        if entity_id_match:
            entity_id_str = entity_id_match.group(1)

            if name and entity_id_str:
                result = SearchResult(
                    entity_id=EntityId(entity_id_str),
                    name=name,
                    similarity_score=0.0,  
                    description=description if description else None
                )
                self.results.append(result)

        # Reset buffers
        self.name_buffer = []
        self.id_buffer = []
        self.description_buffer = []


def _calculate_similarity(query: str, name: str) -> float:
    """
    Calculate similarity score between search query and entity name.
    
    Uses :class:`difflib.SequenceMatcher` to compute a ratio and converts to percentage.
    
    :param query: The search query string
    :type query: :class:`str`
    :param name: The entity name to compare against
    :type name: :class:`str`
    :return: Similarity score as a percentage (0-100)
    :rtype: :class:`float`
    """
    ratio = SequenceMatcher(None, query.lower(), name.lower()).ratio()
    score = ratio * 100
    return score


def suggest_query(query: str, max_suggestions: int = 5) -> List[str]:
    """
    Suggest corrections for misspelled or ambiguous search queries.
    
    This function searches Wikidata and uses the top results to suggest
    similar entity names that might be what the user intended to search for.
    
    :param query: The search query that may contain typos or be ambiguous
    :type query: :class:`str`
    :param max_suggestions: Maximum number of suggestions to return (default: 5)
    :type max_suggestions: :class:`int`
    :return: List of suggested query strings sorted by relevance
    :rtype: :class:`List`\\ [:class:`str`]
    
    """
    try:
        # Search for the query to get similar entity names
        results = _search(query, limit=50)
        
        if not results:
            return []
        
        # Extract entity names from results
        entity_names = [result.name for result in results]
        
        # Use difflib to find close matches
        suggestions = get_close_matches(
            query,
            entity_names,
            n=max_suggestions,
            cutoff=0.6
        )
        
        return suggestions
        
    except Exception as e:
        return []