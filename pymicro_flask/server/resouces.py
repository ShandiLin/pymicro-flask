# -*- coding: utf-8 -*-
import traceback

from flask_restful import Resource
from flask import request, jsonify, abort

from pymicro_flask.config import get_config, get_send_metrics
from pymicro_flask import msg_handler
from pymicro_flask.utils import get_valid_input
from pymicro_flask.server import metrics


import logging
logger = logging.getLogger(__name__)


class MsgProcess(Resource):
    def post(self):
        data = request.get_data()
        jdata, msg = get_valid_input(data)
        if jdata is None:
            abort(400, msg)
        else:
            result = None
            try:
                conf = get_config()
                # define how to handle message here
                result = msg_handler.process_message(jdata)
                jdata.update(result)
            except Exception as e:
                logger.error("process message failed: %s", data)
                logger.error(traceback.format_exc())
                abort(500, traceback.format_exc())
            else:
                return jsonify(jdata)
            finally:
                try:
                    # even exception raise when processing message, corresponding metrics should be increased
                    if get_send_metrics() is False:
                        metrics.inc_metrics(result)
                    elif get_send_metrics() is True:
                        metrics.inc_metrics_statsd(result)
                except Exception as e:
                    logger.error("increase metrics failed: %s", e)
