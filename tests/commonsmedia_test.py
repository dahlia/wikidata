import hashlib
import json
import pathlib

from pytest import fixture

from wikidata.commonsmedia import File

from .mock import MEDIA_FIXTURES_PATH


def test_file_page_url(fx_file: File):
    assert (fx_file.page_url ==
            'https://www.wikidata.org/wiki/File:Gandhara_Buddha_(tnm).jpeg')


def test_file_image_url(fx_file: File):
    assert fx_file.image_url == \
        'https://upload.wikimedia.org/wikipedia/commons/b/b8/Gandhara_Buddha_%28tnm%29.jpeg'  # noqa: E501


def test_file_image_mimetype(fx_file: File):
    assert fx_file.image_mimetype == 'image/jpeg'


def test_file_image_resolution(fx_file: File):
    assert fx_file.image_resolution == (1746, 2894)


def test_file_image_size(fx_file: File):
    assert fx_file.image_size == 823440


@fixture
def fx_file_mock_path(fx_file: File) -> pathlib.Path:
    title_id = hashlib.md5(fx_file.title.encode('utf-8')).hexdigest().lower()
    return MEDIA_FIXTURES_PATH / '{}.json'.format(title_id)


def test_file_attributes(fx_file: File, fx_file_mock_path: pathlib.Path):
    with fx_file_mock_path.open('r') as f:
        assert fx_file.attributes == json.load(f)['query']['pages']['-1']


def test_file_load(fx_file: File, fx_file_mock_path: pathlib.Path):
    fx_file.load()
    with fx_file_mock_path.open('r') as f:
        assert fx_file.data == json.load(f)['query']['pages']['-1']


def test_file_repr(fx_file: File):
    assert (repr(fx_file) ==
            "<wikidata.commonsmedia.File 'File:Gandhara Buddha (tnm).jpeg'>")
