# -*- coding: utf-8 -*-


import re
import random
import datetime

from .utils import (
    normalize_text, expand_regex,
    mapping_inversed, mapping_to_list,
)


TIME_UNIT_MAPPING = dict(
    years=['y', 'year', 'years'],
    months=['month', 'months'],
    weeks=['w', 'wk', 'wks', 'week', 'weeks'],
    days=['d', 'day', 'days'],
    hours=['h', 'hr', 'hrs', 'hour', 'hours'],
    minutes=['m', 'min', 'mins', 'minute', 'minutes'],
    seconds=['s', 'sec', 'secs', 'second', 'seconds'],
    milliseconds=['ms', 'milli', 'millis', 'millisecond', 'milliseconds'],
    microseconds=['microsecond', 'microseconds'],
)

TIME_UNIT_INVERSED_MAPPING = mapping_inversed(TIME_UNIT_MAPPING)

TIME_UNIT_VARIATIONS = mapping_to_list(TIME_UNIT_INVERSED_MAPPING)

REGEX_SUPPORTED_TIME_UNIT_VARIATIONS = re.compile(
    r'|'.join([
        r'\b{}\b'.format(each)
        for each in TIME_UNIT_VARIATIONS
    ]),
    flags=re.UNICODE | re.IGNORECASE
)

REGEX_TIME_UNIT = re.compile(
    r'((?P<value_from>-?\d+(\.\d+)?)'
    r'(\s*to\s*(?P<value_to>-?\d+(\.\d+)?))?\s*)?'
    r'(?P<unit>{})'
    .format(REGEX_SUPPORTED_TIME_UNIT_VARIATIONS.pattern),
    flags=re.UNICODE | re.IGNORECASE
)

REGEX_DURATION = re.compile(
    r'((?P<hours>-?\d+(\.\d+)?)\s*:\s*(?P<minutes>-?\d+(\.\d+)?)'
    r'(\s*:\s*(?P<seconds>-?\d+(\.\d+)?)'
    r'(\s*:\s*(?P<milliseconds>-?\d+(\.\d+)?)'
    r'(\s*\.\s*(?P<microseconds>-?\d+(\.\d+)?))?)?)?)',
    flags=re.UNICODE | re.IGNORECASE
)

REGEX_ISO8601_DURATION = re.compile(
    r'(\s*P\s*'
    r'(\s*(?P<years>-?\d+(\.\d+)?)\s*Y\s*)?'
    r'(\s*(?P<months>-?\d+(\.\d+)?)\s*M\s*)?'
    r'(\s*(?P<weeks>-?\d+(\.\d+)?)\s*W\s*)?'
    r'(\s*(?P<days>-?\d+(\.\d+)?)\s*D\s*)?'
    r'(\s*T\s*'
    r'(\s*(?P<hours>-?\d+(\.\d+)?)\s*H\s*)?'
    r'(\s*(?P<minutes>-?\d+(\.\d+)?)\s*M\s*)?'
    r'(\s*(?P<seconds>-?\d+(\.\d+)?)\s*S\s*)?'
    r')?'
    r')',
    flags=re.UNICODE | re.IGNORECASE
)


def parse(text):
    """Parse time expression.

    :param text: Time expression to parse
    :return: :class:`datetime.timedelta` object
    :rtype: datetime.timedelta
    :raises: TypeError: if text is not a string
    :raises: ValueError: if text is empty
    """
    if not isinstance(text, ("".__class__, u"".__class__)):
        raise TypeError('Expected a string, received: %s' % type(text).__name__)

    text = normalize_text(text)
    if not text:
        raise ValueError('Expected a time expression, recieved an empty string')

    duration_regexs = (REGEX_DURATION, REGEX_ISO8601_DURATION,)
    for duration_regex in duration_regexs:
        text = expand_regex(duration_regex, text, '{value} {name}')

    kwargs = {}
    for match in REGEX_TIME_UNIT.finditer(text):
        unit = match.group('unit').lower()

        value_from = float(match.group('value_from') or '1')
        if match.group('value_to'):
            value_to = float(match.group('value_to'))
            value = random.uniform(value_from, value_to)
        else:
            value = value_from

        unit = TIME_UNIT_INVERSED_MAPPING[unit].lower()
        if unit == 'years':
            unit, value = 'weeks', value * 52
        elif unit == 'months':
            unit, value = 'weeks', value * 4
        elif unit == 'microseconds':
            unit, value = 'milliseconds', value * 0.001

        kwargs[unit] = kwargs.get(unit, 0) + value

    if not kwargs:
        raise ValueError('No time expression recognized')

    return datetime.timedelta(**kwargs)
