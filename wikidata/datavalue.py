""":mod:`wikidata.datavalue` --- Interpreting datavalues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the decoder interface for customizing how datavalues are
decoded, and the default :class:`Decoder` implementation.

Technically the interface is just a callable so that its implementation
doesn't necessarily have to be an instance of :class:`Decoder` or its subclass,
but only need to satify::

    typing.Callable[[wikidata.client.Client, str, typing.Mapping[str, object]],
                    object]

.. versionadded:: 0.3.0

"""
import collections.abc
import datetime
from typing import TYPE_CHECKING, Mapping, Union

from .client import Client
from .commonsmedia import File
from .multilingual import MonolingualText
if TYPE_CHECKING:
    from .entity import Entity  # noqa: F401

__all__ = 'DatavalueError', 'Decoder'


class DatavalueError(ValueError):
    """Exception raised during decoding datavalues.  It subclasses
    :exc:`ValueError` as well.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.args) < 2:
            raise TypeError('expected datavalue from 2nd positional argument')

    @property
    def datavalue(self):
        """The datavalue which caused the decoding error."""
        return self.args[1]

    def __str__(self) -> str:
        message = self.args[0]
        if 'type' in self.datavalue:
            datavalue = dict(self.datavalue)
            type_ = datavalue.pop('type')
            return "{}: {{'type': {!r}, {}}}".format(
                message, type_, repr(datavalue)[1:-1]
            )
        return '{}: {!r}'.format(message, self.datavalue)


class Decoder:
    """Decode the given datavalue to a value of the appropriate Python type.
    For extensibility it uses visitor pattern and is intended to be subclassed.
    To customize decoding of datavalues subclass it and configure
    ``datavalue_decoder`` option of :class:`~.client.Client` to
    the customized decoder.

    It automatically invokes an appropriate visitor method using a simple
    rule of name: ``{datatype}__{datavalue[type]}``.  For example,
    if the following call to a ``decoder`` was made::

        decoder(client, 'mydatatype', {'type': 'mytype', 'value': '...'})

    it's delegated to the following visitor method call:

        decoder.mydatatype__mytype(client, {'type': 'mytype', 'value': '...'})

    If a decoder failed to find a visitor method matched to
    ``{datatype}__{datavalue[type]}`` pattern it secondly try to find
    a general version of visitor method: ``{datavalue[type]}`` which lacks
    double underscores.  For example, for the following call::

        decoder(client, 'mydatatype', {'type': 'mytype', 'value': '...'})

    It firstly try to find the following visitor method:

        decoder.mydatatype__mytype

    but if there's no such method it secondly try to find the following
    general visitor method:

        decoder.mytype

    This twice-try dispatch is useful when to make a visitor method to
    be matched regardless of datatype.

    If its ``datavalue[type]`` contains hyphens they're replaced by
    underscores.  For example::

        decoder(client, 'string',
                {'type': 'wikibase-entityid', 'value': 'a text value'})

    the above call is delegated to the following visitor method call::

        decoder.string__wikibase_entityid(
            #     Note that the ^ underscore
            client,
            {'type': 'wikibase-entityid', 'value': 'a text value'}
        )

    """

    def __call__(self,
                 client: Client,
                 datatype: str,
                 datavalue: Mapping[str, object]) -> object:
        try:
            type_ = datavalue['type']
        except KeyError:
            raise DatavalueError('no "type" specified', datavalue)
        assert isinstance(type_, str)
        if 'value' not in datavalue:
            raise DatavalueError('no "value" field', datavalue)
        method_name = '{}__{}'.format(datatype, type_).replace('-', '_')
        method = getattr(self, method_name, None)
        if callable(method):
            return method(client, datavalue)
        method_name = type_.replace('-', '_')
        method = getattr(self, method_name, None)
        if callable(method):
            return method(client, datavalue)
        raise DatavalueError('{!r} is unsupported type'.format(type_),
                             datavalue)

    def wikibase_entityid(self,
                          client: Client,
                          datavalue: Mapping[str, object]) -> 'Entity':
        val = datavalue['value']
        if not isinstance(val, collections.abc.Mapping):
            raise DatavalueError('expected a dictionary, not {!r}'.format(val),
                                 datavalue)
        try:
            id_ = val['id']
        except KeyError:
            raise DatavalueError('no "id" field', datavalue)
        return client.get(id_)

    def string(self, client: Client, datavalue: Mapping[str, object]) -> str:
        value = datavalue['value']
        assert isinstance(value, str)
        return value

    def time(self,
             client: Client,
             datavalue: Mapping[str, object]) -> Union[datetime.date,
                                                       datetime.datetime]:
        value = datavalue['value']
        if not isinstance(value, collections.abc.Mapping):
            raise DatavalueError(
                'expected a dictionary, not {!r}'.format(value),
                datavalue
            )
        try:
            cal = value['calendarmodel']
        except KeyError:
            raise DatavalueError('missing "calendarmodel" field', datavalue)
        if cal != 'http://www.wikidata.org/entity/Q1985727':
            raise DatavalueError('{!r} is unsupported calendarmodel for time '
                                 'datavalue'.format(cal), datavalue)
        try:
            time = value['time']
        except KeyError:
            raise DatavalueError('missing "time" field', datavalue)
        if time[0] != '+':
            raise DatavalueError(
                '{!r}: only AD (CE) is supported'.format(time),
                datavalue
            )
        try:
            tz = value['timezone']
        except KeyError:
            raise DatavalueError('missing "timezone" field', datavalue)
        if tz != 0:
            raise DatavalueError(
                '{!r}: timezone other than 0 is unsupported'.format(
                    value['timezone']
                ),
                datavalue
            )
        if 'before' not in value or 'after' not in value:
            raise DatavalueError('before/after field is missing', datavalue)
        elif value['before'] != 0 or value['after'] != 0:
            raise DatavalueError(
                'uncertainty range time (represented using before/'
                'after) is unsupported',
                datavalue
            )
        try:
            precision = value['precision']
        except KeyError:
            raise DatavalueError('precision field is missing', datavalue)
        if precision == 11:
            return datetime.date(int(time[1:5]), int(time[6:8]),
                                 int(time[9:11]))
        elif precision == 14:
            return datetime.datetime.strptime(
                time[1:],
                '%Y-%m-%dT%H:%M:%SZ'
            ).replace(tzinfo=datetime.timezone.utc)
        else:
            raise DatavalueError(
                '{!r}: time precision other than 11 or 14 is '
                'unsupported'.format(precision),
                datavalue
            )

    def monolingualtext(self,
                        client: Client,
                        datavalue: Mapping[str, object]) -> MonolingualText:
        pair = datavalue['value']
        return MonolingualText(pair['text'], pair['language'])  # type: ignore

    def commonsMedia__string(self,
                             client: Client,
                             datavalue: Mapping[str, object]) -> File:
        return File(client, 'File:{0}'.format(datavalue['value']))
