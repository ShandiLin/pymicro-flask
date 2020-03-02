from __future__ import print_function
from __future__ import unicode_literals

import json
import time

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    # python 2
    from urlparse import urlparse

from pymicro_flask.ret_code import *

import logging
logger = logging.getLogger(__name__)


def parse_json(val):
    try:
        json_object = json.loads(val)
    except ValueError as e:
        return None
    return json_object


def parse_url(url):
    return urlparse(url)


def get_valid_input(data):
    '''
        check if input json string is valid, only return value when data is
        a valid JSON object with only one item
    '''
    jdata = parse_json(data)
    if jdata is None:
        logger.error("get non json format data: %s", data)
        return None, "input should be JSON object"
    elif not isinstance(jdata, dict):
        logger.error("message should be a single json object, get: %s", data)
        return None, "input should be single JSON object"
    return jdata, None


def is_valid_url(url):
    parsed_url = parse_url(url)
    try:
        parsed_url.port
        return all([parsed_url.scheme, parsed_url.hostname])
    except ValueError:
        return False


def str2bool(val):
    try:
        eval_val = eval(val.capitalize())
        if isinstance(eval_val, bool):
            return eval_val
        return None
    except:
        logger.error("value '%s' can not be eval as boolean", val)
        return None
