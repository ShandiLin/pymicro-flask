# -*- coding: utf-8 -*-

from pymicro_flask.server.metrics import *
from pymicro_flask.server.app import create_app
from pymicro_flask.ret_code import *

from tutils import CompareMetrics, FakeSocket


@CompareMetrics({
    PYMC_REQ: 1,
}, 200)
def test_inc_metrics_req_total_success():
    inc_metrics(code=200)

@CompareMetrics({
    PYMC_REQ: 1,
}, 500)
def test_inc_metrics_req_total_fail():
    inc_metrics(code=500)


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
    inc_metrics_statsd(code=200, statsd=statsd)

    assert statsd.socket.recv() == '{s}:1|c|#code:{v}'.format(
        s=PYMC_REQ, v=200)

def test_inc_metrics_statsd_fail():
    statsd = DogStatsd()
    statsd.socket = FakeSocket()
    inc_metrics_statsd(code=500, statsd=statsd)

    assert statsd.socket.recv() == '{s}:1|c|#code:{v}'.format(
        s=PYMC_REQ, v=500)
