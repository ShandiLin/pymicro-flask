# -*- coding: utf-8 -*-
from __future__ import print_function


from pymicro_flask.server.metrics import *
from pymicro_flask.server.app import create_app
from pymicro_flask.ret_code import *

from tutils import CompareMetrics, FakeSocket


MKEY_RET = KEY_RET.replace('.', '_')

def success_return():
    return {
        KEY_E_TIME: "1581347950.82",
        KEY_RET: RET_SUCCESS,
        KEY_S_TIME: "1581347950.82",
    }

def fail_return():
    return {
        KEY_E_TIME: "1581347950.82",
        KEY_RET: RET_FAILED,
        KEY_S_TIME: "1581347950.82",
    }


@CompareMetrics({
    PYMC_REQ: 1,
    PYMC_RET_REQ: 1,
}, RET_SUCCESS)
def test_inc_metrics_req_total_success():
    # only add request total
    result = success_return()
    inc_metrics(result)

@CompareMetrics({
    PYMC_REQ: 1,
    PYMC_RET_REQ: 1,
}, RET_FAILED)
def test_inc_metrics_req_total_fail():
    # only add request total
    result = fail_return()
    inc_metrics(result)


from werkzeug.test import create_environ
from werkzeug.test import run_wsgi_app


def test_setup_metrics():
    app = create_app()
    app_dispatch = setup_metrics(app)
    app_iter, status, headers = run_wsgi_app(app_dispatch, create_environ("/metrics"))
    assert status == "200 OK"


def test_inc_metrics_statsd_success():
    statsd = DogStatsd()
    statsd.socket = FakeSocket()
    result = success_return()
    inc_metrics_statsd(result, statsd=statsd)

    assert statsd.socket.recv() == '{s}:1|c'.format(s=PYMC_REQ)
    assert statsd.socket.recv() == '{s}:1|c|#{k}:{v}'.format(
        k=MKEY_RET, s=PYMC_RET_REQ, v=RET_SUCCESS)


def test_inc_metrics_statsd_fail():
    statsd = DogStatsd()
    statsd.socket = FakeSocket()
    result = fail_return()
    inc_metrics_statsd(result, statsd=statsd)

    assert statsd.socket.recv() == '{s}:1|c'.format(s=PYMC_REQ)
    assert statsd.socket.recv() == '{s}:1|c|#{k}:{v}'.format(
        k=MKEY_RET, s=PYMC_RET_REQ, v=RET_FAILED)
