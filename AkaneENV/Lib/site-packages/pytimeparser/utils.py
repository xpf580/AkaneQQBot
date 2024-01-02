# -*- coding: utf-8 -*-

"""Utility functions"""


import re
import string


def remove_whitespace(text):
    """Remove all whitespace."""
    return re.sub(r'(\s)+', '', text, flags=re.UNICODE)


def normalize_whitespace(text, replace_with=' '):
    """Normalize whitespace."""
    text = re.sub(r'(\s)+', replace_with, text, flags=re.UNICODE)
    text = re.sub(
        r'\s*([{}])\s*'.format(string.punctuation), '\\1 ',
        text, flags=re.UNICODE
    )
    return text.strip()


def normalize_numbers(text):
    """Normalize numbers."""
    def normalize_number(match):
        number = match.group('number')
        number = remove_whitespace(number)
        number = number.replace(',', '.')
        return ' ' + number + ' '

    text = re.sub(
        r'(?P<number>(\s*[+-]\s*)?(\s*\d+\s*)+(\s*[.,]\s*\d+\s*)?)',
        normalize_number, text, flags=re.UNICODE
    )
    return text.strip()


def normalize_text(text):
    """Normalize text by normalizing whitespace and numbers."""
    text = normalize_whitespace(text)
    text = normalize_numbers(text)
    return text.strip()


def expand_regex(regex, text, template, sep=' '):
    """Expand regex using provided template"""
    for match in regex.finditer(text):
        value = sep.join([
            template.format(name=name, value=value)
            for name, value in match.groupdict().items()
            if value and value.strip()
        ])
        text = regex.sub(value, text)
    return text


def mapping_inversed(mapping):
    """Inverse a mapping of lists"""
    return {value: key for key in mapping for value in mapping[key]}


def mapping_to_list(mapping):
    """Convert a mapping to a list"""
    output = []
    for key, value in mapping.items():
        output.extend([key, value])
    return output
