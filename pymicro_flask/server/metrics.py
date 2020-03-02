# -*- coding: utf-8 -*-
import os
from datadog import DogStatsd
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from pymicro_flask.config import get_statsd_server
from pymicro_flask.ret_code import *


MKEY_RET = KEY_RET.replace('.', '_')

# statsd client
statsd = DogStatsd(host=get_statsd_server().hostname, port=get_statsd_server().port)

# Counter Key Name
PYMC = 'pymicro'
PYMC_REQ = '{p}_req_total'.format(p=PYMC)
PYMC_RET_REQ = '{p}_ret_req_total'.format(p=PYMC)

# Counter for prometheus_client
REQ_CNT = Counter(PYMC_REQ, 'Request count')
RET_REQ_CNT = Counter(PYMC_RET_REQ, 'Request return code count', [MKEY_RET])


def setup_metrics(app):
    '''
        When SEND_METRICS is False, add prometheus wsgi middleware to
        route /metrics requests
    '''
    app_dispatch = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })
    return app_dispatch


def inc_metrics(result):
    '''
        Use prometheus_client library to update the metrics hold by application
        invoked when SEND_METRICS is False
    '''
    REQ_CNT.inc()
    if result is not None and result.get(KEY_RET) is not None:
       RET_REQ_CNT.labels(result.get(KEY_RET)).inc()

def inc_metrics_statsd(result, statsd=statsd):
    '''
        Use datadog library to send metrics to stastd node-exporter
        invoked when SEND_METRICS is True
    '''
    statsd.increment(PYMC_REQ)
    if result is not None and result.get(KEY_RET) is not None:
        statsd.increment(PYMC_RET_REQ,
            tags=[":".join([MKEY_RET, str(result.get(KEY_RET))])])
