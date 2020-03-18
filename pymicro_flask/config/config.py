# -*- coding: utf-8 -*-
import os
import sys
import warnings

from pymicro_flask.config.parser import DefaultConfigParser, PymicroConfigError
from pymicro_flask.utils import is_valid_url, parse_url, str2bool


class DefaultConfig(object):

    def __init__(self):
        try:
            if not os.environ.get("PYMICRO_DATADIR"):
                os.environ["PYMICRO_DATADIR"] = "/tmp"
            root_dirpath = sys.exec_prefix
            cp = DefaultConfigParser(os.path.join(root_dirpath, "conf/service.toml"))
            self._conf = cp.read()
        except PymicroConfigError as e:
            raise

    @property
    def conf(self):
        return self._conf

    def get_server(self):
        return parse_url(self.conf["server"]["pymicro_server"])

    def get_send_metrics(self):
        return self.conf["statsd"]["send_metrics"]

    def get_statsd_server(self):
        return parse_url(self.conf["statsd"]["pymicro_statsd"])

    def print_server_config(self):
        SERVER = self.get_server()
        STATSD_SERVER = self.get_statsd_server()
        print("PYMICRO_SERVER={s}".format(s=SERVER.geturl()))
        print("PYMICRO_HOST={s}".format(s=SERVER.hostname))
        print("PYMICRO_PORT={s}".format(s=SERVER.port))
        print("PYMICRO_SEND_METRICS={s}".format(s=str(self.get_send_metrics()).lower()))
        print("PYMICRO_STATSD={s}".format(s=STATSD_SERVER.geturl()))
        print("PYMICRO_STATSD_HOST={s}".format(s=STATSD_SERVER.hostname))
        print("PYMICRO_STATSD_PORT={s}".format(s=STATSD_SERVER.port))


class PymicroConfig(DefaultConfig):
    '''
        Config Read Priority:
            1. param: conf_path
            2. $PYMICRO_CONFIG
            3. default config: conf/service.toml
    '''
    def __init__(self, conf_path=None):
        try:
            if conf_path:
                cp = DefaultConfigParser(conf_path)
                self._conf = cp.read()
            else:
                if not os.environ.get("PYMICRO_CONFIG"):
                    super(PymicroConfig, self).__init__()
                else:
                    cp = DefaultConfigParser(os.environ.get("PYMICRO_CONFIG"))
                    self._conf = cp.read()

            if os.environ.get("PYMICRO_SERVER") is not None:
                if is_valid_url(os.environ.get("PYMICRO_SERVER")) is True:
                    self._conf["server"]["pymicro_server"] = os.environ.get("PYMICRO_SERVER")
                else:
                    warnings.warn("PYMICRO_SERVER not valid url, using default: %s" %
                        self._conf["server"]["pymicro_server"], UserWarning)

            if os.environ.get("PYMICRO_SEND_METRICS") is not None:
                tmp_send_metrics = str2bool(os.environ.get("PYMICRO_SEND_METRICS"))
                if tmp_send_metrics is not None:
                    self._conf["statsd"]["send_metrics"] = tmp_send_metrics
                else:
                    warnings.warn("PYMICRO_SEND_METRICS not boolean, using default: %s" %
                        self._conf["statsd"]["send_metrics"], UserWarning)

            if os.environ.get("PYMICRO_STATSD") is not None:
                if is_valid_url(os.environ.get("PYMICRO_STATSD")) is True:
                    self._conf["statsd"]["pymicro_statsd"] = os.environ.get("PYMICRO_STATSD")
                else:
                    warnings.warn("PYMICRO_STATSD not valid url, using default: %s" %
                        self._conf["statsd"]["pymicro_statsd"], UserWarning)
        except PymicroConfigError as e:
            raise


pymicro_conf = PymicroConfig()
