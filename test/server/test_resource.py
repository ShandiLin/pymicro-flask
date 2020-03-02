# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import logging
import random

from pymicro_flask.ret_code import *

from tutils import test_client


PYMICRO_API_PATH = '/microservice'


def test_pymicro_post_400(test_client, mocker):
    '''
        Input post data is invalid for pymicro to parse, return 400
    '''
    invalid_data_list = [
        'hello pymicro',            # should be json format
        '[{"abc":"def"}]',          # only one json object is available
    ]
    for send_metrics, metrics_mock in [
        ("False", mocker.patch('pymicro_flask.server.metrics.inc_metrics', return_value=None)),
        ("True", mocker.patch('pymicro_flask.server.metrics.inc_metrics_statsd', return_value=None))
    ]:
        os.environ["PYMICRO_SEND_METRICS"] = send_metrics
        for data in invalid_data_list:
            response = test_client.post(PYMICRO_API_PATH, data=data)
            assert response.status_code == 400
            assert metrics_mock.call_count == 0


def test_pymicro_post_200(test_client, mocker):
    '''
        message return with SUCCESS/FAIDED
    '''
    data = '{"abc":"def"}'
    for send_metrics, metrics_mock in [
        ("False", mocker.patch('pymicro_flask.server.metrics.inc_metrics', return_value=None)),
        ("True", mocker.patch('pymicro_flask.server.metrics.inc_metrics_statsd', return_value=None))
    ]:
        os.environ["PYMICRO_SEND_METRICS"] = send_metrics
        mocker.patch('random.randint', return_value=2)
        response = test_client.post(PYMICRO_API_PATH, data=data)
        assert response.status_code == 200
        assert KEY_S_TIME in response.json and KEY_E_TIME in response.json
        assert response.json.get(KEY_RET) == 0
        assert metrics_mock.call_count == 1

        mocker.patch('random.randint', return_value=3)
        response = test_client.post(PYMICRO_API_PATH, data=data)
        assert response.status_code == 200
        assert KEY_S_TIME in response.json and KEY_E_TIME in response.json
        assert response.json.get(KEY_RET) == -1
        assert metrics_mock.call_count == 2


def test_pymicro_post_exception(test_client, mocker):
    '''
        Pymico_flask should return 500 if any exception raised in processing messages.
        However, the metrics will still updated (increase pymicro_req_total counter)
    '''
    data = '{"abc":"def"}'
    for send_metrics, metrics_mock in [
        ("False", mocker.patch('pymicro_flask.server.metrics.inc_metrics', return_value=None)),
        ("True", mocker.patch('pymicro_flask.server.metrics.inc_metrics_statsd', return_value=None))
    ]:
        os.environ["PYMICRO_SEND_METRICS"] = send_metrics
        mocker.patch('pymicro_flask.msg_handler.process_message', side_effect=Exception('mocked error'))
        response = test_client.post(PYMICRO_API_PATH, data=data)
        assert response.status_code == 500
        assert metrics_mock.call_count == 1


def test_pymicro_send_metrics_exception(test_client, mocker):
    '''
        If getting exception when updating metrics, pymicro_flask will log error
    '''
    data = '{"abc":"def"}'
    for send_metrics, metrics_mock in [
        ("False", mocker.patch('pymicro_flask.server.metrics.inc_metrics', side_effect=Exception('mocked error'))),
        ("True", mocker.patch('pymicro_flask.server.metrics.inc_metrics_statsd', side_effect=Exception('mocked error')))
    ]:
        os.environ["PYMICRO_SEND_METRICS"] = send_metrics
        logger_mock = mocker.patch.object(logging.getLogger('pymicro_flask.server.resouces'), 'error')
        response = test_client.post(PYMICRO_API_PATH, data=data)
        assert response.status_code == 200
        assert metrics_mock.call_count == 1
        assert logger_mock.call_count == 1
