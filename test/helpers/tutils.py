# -*- coding: utf-8 -*-

from collections import deque
import socket
import pytest

from prometheus_client import REGISTRY
from datadog.util.compat import is_p3k

from pymicro_flask.config import get_config
from pymicro_flask.server.app import create_app
from pymicro_flask.server.metrics import *
from pymicro_flask.ret_code import *


MKEY_RET = KEY_RET.replace('.', '_')
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_data"
)


def reload_config():
    import pymicro_flask
    try:
        # python 2
        reload(pymicro_flask.config)
    except:
        # python 3
        import importlib
        importlib.reload(pymicro_flask.config)


@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield testing_client

    ctx.pop()


METRICS_KEYS = [
    PYMC_REQ
]

METRICS_TAGS_KEYS = [
    PYMC_RET_REQ
]

class CompareMetrics(object):
    def __init__(self, compare_dict, ret):
        self.compare_dict = compare_dict
        self.ret = ret

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            before = dict()
            for key in METRICS_KEYS:
                before[key] = int(REGISTRY.get_sample_value(key) or 0.0)
            for key in METRICS_TAGS_KEYS:
                print({MKEY_RET: self.ret})
                print("before:",REGISTRY.get_sample_value(key, {MKEY_RET: self.ret}))
                before[key] = int(REGISTRY.get_sample_value(
                    key, {MKEY_RET: str(self.ret)}) or 0.0)
            # increase corresponding metrics depends on result
            func()
            result = dict()
            for key in METRICS_KEYS:
                result[key] = int(REGISTRY.get_sample_value(key) or 0.0) - before[key]
            for key in METRICS_TAGS_KEYS:
                print("after:", REGISTRY.get_sample_value(key, {MKEY_RET: self.ret}))
                result[key] = int(REGISTRY.get_sample_value(
                    key, {MKEY_RET: str(self.ret)}) or 0.0) - before[key]
            assert self.compare_dict == result
        return wrapper


# https://github.com/DataDog/datadogpy/blob/master/tests/unit/dogstatsd/test_statsd.py
class FakeSocket(object):
    """ A fake socket for testing. """

    def __init__(self):
        self.payloads = deque()

    def send(self, payload):
        if is_p3k():
            assert type(payload) == bytes
        else:
            assert type(payload) == str
        self.payloads.append(payload)

    def recv(self):
        try:
            return self.payloads.popleft().decode('utf-8')
        except IndexError:
            return None

    def close(self):
        pass

    def __repr__(self):
        return str(self.payloads)
