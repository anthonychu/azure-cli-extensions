import os

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.util import get_file_json, shell_safe_json_parse


def parse_json_arg(value, argument_name='--body'):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    try:
        if value.startswith('@'):
            return get_file_json(value[1:], throw_on_empty=False)
        if os.path.isfile(value):
            return get_file_json(value, throw_on_empty=False)
        return shell_safe_json_parse(value)
    except Exception as ex:  # pylint: disable=broad-except
        raise InvalidArgumentValueError('Unable to parse {} as JSON: {}'.format(argument_name, ex))


def parse_key_value_pairs(values):
    pairs = []
    for item in values or []:
        if '=' not in item:
            raise InvalidArgumentValueError("Expected NAME=VALUE, but received '{}'".format(item))
        name, value = item.split('=', 1)
        if not name:
            raise InvalidArgumentValueError("Expected a non-empty parameter name in '{}'".format(item))
        pairs.append({'name': name, 'value': value})
    return pairs


def ensure_object(value, argument_name='--body'):
    parsed = parse_json_arg(value, argument_name)
    if parsed is not None and not isinstance(parsed, dict):
        raise InvalidArgumentValueError('{} must be a JSON object.'.format(argument_name))
    return parsed