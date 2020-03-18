# -*- coding: utf-8 -*-
import os
from datadog import DogStatsd
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from pymicro_flask.config.config import pymicro_conf
from pymicro_flask.ret_code import *


MKEY_RET = KEY_RET.replace('.', '_')

# statsd client
statsd_server = pymicro_conf.get_statsd_server()
statsd = DogStatsd(host=statsd_server.hostname, port=statsd_server.port)

# Counter Key Name
PYMC = 'pymicro'
PYMC_REQ = '{p}_req_total'.format(p=PYMC)

# Counter for prometheus_client
REQ_CNT = Counter(PYMC_REQ, 'Request count', ["code"])


def setup_metrics(app):
    '''
        When SEND_METRICS is False, add prometheus wsgi middleware to
        route /metrics requests
    '''
    app_dispatch = DispatcherMiddleware(app, {
        '/metrics': make_wsgi_app()
    })
    return app_dispatch


def inc_metrics(code=None):
    '''
        Use prometheus_client library to update the metrics hold by application
        invoked when SEND_METRICS is False
    '''
    REQ_CNT.labels(code=str(code).lower()).inc()


def inc_metrics_statsd(code=None, statsd=statsd):
    '''
        Use datadog library to send metrics to stastd node-exporter
        invoked when SEND_METRICS is True
    '''
    code_tag_name = "code:" + str(code).lower()
    statsd.increment(PYMC_REQ, tags=[code_tag_name])
