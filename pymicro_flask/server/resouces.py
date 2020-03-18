# -*- coding: utf-8 -*-
import traceback

from flask_restful import Resource
from flask import request, jsonify, abort
from werkzeug.exceptions import HTTPException

from pymicro_flask.config.config import pymicro_conf
from pymicro_flask import msg_handler
from pymicro_flask.utils import get_valid_input
from pymicro_flask.server import metrics


import logging
logger = logging.getLogger(__name__)


class MsgProcess(Resource):
    def post(self):
        result = None
        resp_code = None
        try:
            data = request.get_data()
            jdata, msg = get_valid_input(data)
            if jdata is None:
                resp_code = 400
                abort(resp_code, msg)
            else:
                # define how to handle message here
                result = msg_handler.process_message(jdata)
                jdata.update(result)
                resp_code = 200
                return jsonify(jdata)
        except HTTPException as e:
            resp_code = e.get_response().status_code
            abort(resp_code, msg)
        except Exception as e:
            logger.error("process message failed: %s", data)
            logger.error(traceback.format_exc())
            resp_code = 500
            abort(resp_code, traceback.format_exc())
        finally:
            try:
                # even exception raise when processing message, corresponding metrics should be increased
                send_metrics = pymicro_conf.get_send_metrics()
                if send_metrics is False:
                    metrics.inc_metrics(code=resp_code)
                elif send_metrics is True:
                    metrics.inc_metrics_statsd(code=resp_code)
            except Exception as e:
                logger.error("increase metrics failed: %s", e)
