from __future__ import unicode_literals

import json
import pytest

from pymicro_flask.utils import parse_json, parse_url, is_valid_url, \
                                    get_valid_input, str2bool
from pymicro_flask.ret_code import *


def test_parse_json():
    data = '[{"url": "abc"}]'
    assert parse_json(data)[0]["url"] == "abc"

    data = '{"123"}'
    assert parse_json(data) is None


def test_is_valid_url():
    data = "http://www.google.com"
    assert is_valid_url(data) is True

    data = "http://0.0.0.0:80"
    assert is_valid_url(data) is True

    # port is not int
    data = "http://0.0.0.0:abc"
    assert is_valid_url(data) is False

    # no scheme
    data = "www.google.com"
    assert is_valid_url(data) is False

    # no hostname
    data = "http://:8080"
    assert is_valid_url(data) is False


def test_get_valid_input():
    data = "abc"
    jdata, ret = get_valid_input(data)
    assert jdata is None
    assert ret == "input should be JSON object"

    data = json.dumps([{"abc": "def"}])
    jdata, ret = get_valid_input(data)
    assert jdata is None
    assert ret == "input should be single JSON object"

    data = json.dumps({"abc": "def"})
    jdata, ret = get_valid_input(data)
    assert jdata == {"abc": "def"}


def test_str2bool():
    for data in ["True", "true", "TRUE"]:
        assert str2bool(data) == True
    for data in ["False", "false", "FALSE"]:
        assert str2bool(data) == False
    for data in ["abc", 123]:
        assert str2bool(data) is None


def test_parse_url():
    try:
        # python 3
        from urllib.parse import urlparse
    except ImportError:
        # python 2
        from urlparse import urlparse

    data = "http://www.google.com"
    assert parse_url(data) == urlparse(data)
