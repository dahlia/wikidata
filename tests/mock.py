import http.client
import io
import logging
import pathlib
import socket
import urllib.error
import urllib.parse
import urllib.request
import urllib.response

__all__ = 'FIXTURES_PATH', 'FixtureOpener'


FIXTURES_PATH = pathlib.Path(__file__).parent / 'fixtures'


class FixtureOpener(urllib.request.OpenerDirector):

    def __init__(self, base_url: str) -> None:
        self.base_url = urllib.parse.urlparse(
            urllib.parse.urljoin(base_url, './Special:EntityData/')
        )
        cls = type(self)
        self.logger = logging.getLogger(cls.__qualname__) \
                             .getChild(cls.__name__)

    def open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        logger = self.logger.getChild('open')
        if not isinstance(fullurl, str):
            fullurl = fullurl.get_full_url()
        parsed = urllib.parse.urlparse(fullurl)
        hdrs = http.client.HTTPMessage()
        path = None
        found = (
            parsed.scheme.lower() == self.base_url.scheme.lower() and
            parsed.username == self.base_url.username and
            parsed.password == self.base_url.password and
            parsed.hostname.lower() == self.base_url.hostname.lower() and
            parsed.port == self.base_url.port and
            parsed.path.startswith(self.base_url.path) and
            parsed.path.endswith('.json')
        )
        if found:
            entity_id = parsed.path[len(self.base_url.path):-5]
            found = entity_id[0].isupper() and entity_id[1:].isdigit()
            if found:
                path = FIXTURES_PATH / (entity_id + '.json')
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
