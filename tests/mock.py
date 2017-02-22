import hashlib
import http.client
import io
import json
import logging
import pathlib
import socket
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

__all__ = ('ENTITY_FIXTURES_PATH', 'FIXTURES_PATH', 'MEDIA_FIXTURES_PATH',
           'FixtureOpener')


FIXTURES_PATH = pathlib.Path(__file__).parent / 'fixtures'
ENTITY_FIXTURES_PATH = FIXTURES_PATH / 'entities'
MEDIA_FIXTURES_PATH = FIXTURES_PATH / 'media'


class FixtureOpener(urllib.request.OpenerDirector):

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.entities_base_url = urllib.parse.urlparse(
            urllib.parse.urljoin(base_url, './wiki/Special:EntityData/')
        )
        self.media_base_url = urllib.parse.urlparse(
            urllib.parse.urljoin(base_url, './w/api.php')
        )
        # ./w/api.php?action=query&prop=imageinfo|info&inprop=url&iiprop=url|size|mime&format=json&titles={}  # noqa: E501
        cls = type(self)
        self.logger = logging.getLogger(cls.__qualname__) \
                             .getChild(cls.__name__)

    @staticmethod
    def match_netloc(a: urllib.parse.ParseResult,
                     b: urllib.parse.ParseResult) -> bool:
        return (a.scheme.lower() == b.scheme.lower() and
                a.username == b.username and
                a.password == b.password and
                a.hostname.lower() == b.hostname.lower() and
                a.port == b.port)

    def open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        logger = self.logger.getChild('open')
        if not isinstance(fullurl, str):
            fullurl = fullurl.get_full_url()
        parsed = urllib.parse.urlparse(fullurl)
        hdrs = http.client.HTTPMessage()
        # media fixtures
        if self.match_netloc(parsed, self.media_base_url) and \
           parsed.path == self.media_base_url.path:
            qs = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
            if not (qs['action'] == ['query'] and
                    len(qs['prop']) == 1 and
                    set(qs['prop'][0].split('|')) == {'imageinfo', 'info'} and
                    qs['inprop'] == ['url'] and
                    len(qs['iiprop']) == 1 and
                    set(qs['iiprop'][0].split('|')) ==
                    {'url', 'size', 'mime'} and
                    qs['format'] == ['json'] and
                    'titles' in qs and
                    len(qs['titles']) == 1):
                hdrs.add_header('Content-Type', 'application/json')
                fp = io.BytesIO(
                    json.dumps({
                        'error': {'*': '...', 'code': '...', 'info': '...'},
                        'servedby': '...',
                    }).encode('utf-8')
                )
                return urllib.response.addinfourl(fp, hdrs, fullurl, 200)
            title, = qs['titles']
            title_id = hashlib.md5(title.encode('utf-8')).hexdigest().lower()
            path = MEDIA_FIXTURES_PATH / (title_id + '.json')
            if path.is_file():
                fp = path.open('rb')
            else:
                result = {
                    'batchcomplete': '',
                    'query': {
                        'pages': {
                            '-1': {
                                'imagerepository': '',
                                'missing': '',
                                'ns': 6,
                                'title': title,
                            }
                        }
                    }
                }
                fp = io.BytesIO(json.dumps(result).encode('utf-8'))
                path = path.relative_to(pathlib.Path.cwd())
                logger.warn("Couldn't find %s; to add a new fixture file "
                            'download it from Wikidata website:\n  '
                            'curl -o %s "%s"',
                            path, path, fullurl)
            hdrs.add_header('Content-Type', 'application/json')
            return urllib.response.addinfourl(fp, hdrs, fullurl, 200)
        # entity fixtures
        path = None
        found = (self.match_netloc(parsed, self.entities_base_url) and
                 parsed.path.startswith(self.entities_base_url.path) and
                 parsed.path.endswith('.json'))
        if found:
            entity_id = parsed.path[len(self.entities_base_url.path):-5]
            found = entity_id[0].isupper() and entity_id[1:].isdigit()
            if found:
                path = ENTITY_FIXTURES_PATH / (entity_id + '.json')
                found = path.is_file()
        if found:
            fp = path.open('rb')
            hdrs.add_header('Content-Type', 'application/json')
            return urllib.response.addinfourl(fp, hdrs, fullurl, 200)
        if path:
            path = path.relative_to(pathlib.Path.cwd())
            logger.warn("Couldn't find %s; to add a new fixture file "
                        'download it from Wikidata website:\n  '
                        'curl -o %s %s',
                        path, path, fullurl)
        hdrs.add_header('Content-Type', 'text/plain; charset=utf-8')
        fp = io.BytesIO(b'Not Found: ' + fullurl.encode())
        raise urllib.error.HTTPError(fullurl, 404, 'Not Found', hdrs, fp)
