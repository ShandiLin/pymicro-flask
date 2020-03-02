# -*- coding: utf-8 -*-
import errno
import os
import re
import shutil
import six
import sys
import toml
import traceback

from pymicro_flask.utils import is_valid_url, parse_url, str2bool


class BaseConfigParser(object):

    def __init__(self, conf_path):
        self.conf_path = conf_path

    def _preprocess(self, conf_obj):
        # validate setting
        pass

    def _check_string(self, key, val):
        if not isinstance(val, six.string_types):
            raise pymicroConfigError(
                "'{k}' should be defined and type of value should be string." \
                    .format(k=key)
            )

    def _check_bool(self, key, val):
        if not isinstance(val, bool):
            raise pymicroConfigError(
                "'{k}' should be defined and type of value should be boolean." \
                    .format(k=key)
            )

    def _check_section_exist(self, conf, key, sub_keys):
        if conf.get(key) is None:
            raise pymicroConfigError(
                "'{k}' should be set as section and contains key_list {ks}." \
                    .format(k=key, ks=sub_keys)
            )
        return conf.get(key)

    def _check_valid_url(self, key, val):
        if is_valid_url(val) is False:
            raise pymicroConfigError(
                "'{k}' should be valid url, get {v}" \
                    .format(k=key, v=val)
            )

    def read(self):
        try:
            with open(self.conf_path, 'rb') as f:
                conf_obj = toml.load(self.conf_path)
            self._preprocess(conf_obj)
        except Exception as e:
            raise
        else:
            return conf_obj


class GlobalConfigParser(BaseConfigParser):

    def __init__(self, conf_path):
        super(GlobalConfigParser, self).__init__(conf_path)

    def _preprocess(self, conf_obj):
        try:
            # check server
            server_sec = self._check_section_exist(conf_obj, "server", ["pymicro"])
            self._check_string("pymicro", server_sec.get("pymicro"))
            self._check_valid_url("pymicro", server_sec.get("pymicro"))

            # check statsd (metrics)
            statsd_sec = self._check_section_exist(conf_obj, "statsd", ["pymicro_statsd", "send_metrics"])
            self._check_bool("send_metrics", statsd_sec.get("send_metrics"))
            self._check_string("pymicro_statsd", statsd_sec.get("pymicro_statsd"))
            self._check_valid_url("pymicro_statsd", statsd_sec.get("pymicro_statsd"))

            # check output path
            output_sec = self._check_section_exist(conf_obj, "output", ["data_dir"])
            self._check_string("data_dir", output_sec.get("data_dir"))
            # expand the path for output directory
            for k in conf_obj.get('output'):
                conf_obj["output"][k] = os.path.expandvars(conf_obj["output"][k])
                if '$' in conf_obj["output"][k]:
                    conf_obj["output"][k] = None
                if conf_obj["output"][k] is None:
                    raise pymicroConfigError("check config value of " + k)
            if is_permission_denied(conf_obj["output"]["data_dir"]) is True:
                raise pymicroConfigError("can not create folder for data, path: " + \
                    conf_obj["output"]["data_dir"])
        except pymicroConfigError as e:
            raise


class pymicroConfigError(Exception):
    pass


def is_permission_denied(fpath):
    if os.path.exists(fpath) is False:
        try:
            # check if path can be created if not exists
            os.makedirs(fpath)
            shutil.rmtree(fpath, ignore_errors=True)
            return False
        except OSError as e:
            if e.errno != errno.EEXIST:
                traceback.print_exc()
                return True
            else:
                return False
    return False


def get_config(conf_fpath=None):
    if not os.environ.get("PYMICRO_DATADIR"):
        os.environ["PYMICRO_DATADIR"] = "/tmp"

    # get where the script installed
    root_dirpath = sys.exec_prefix
    conf_fpath = conf_fpath or os.path.join(root_dirpath, "conf/service.toml")
    cp = GlobalConfigParser(conf_fpath)
    conf = cp.read()

    # replace value from environment variable
    if os.environ.get("PYMICRO") is not None and \
        is_valid_url(os.environ.get("PYMICRO")) is True:
        conf["server"]["pymicro"] = os.environ.get("PYMICRO")

    if os.environ.get("PYMICRO_SEND_METRICS") is not None:
        tmp_send_metrics = str2bool(os.environ.get("PYMICRO_SEND_METRICS"))
        if tmp_send_metrics is not None:
            conf["statsd"]["send_metrics"] = tmp_send_metrics

    if os.environ.get("PYMICRO_STATSD") is not None and \
        is_valid_url(os.environ.get("PYMICRO_STATSD")) is True:
        conf["statsd"]["pymicro_statsd"] = os.environ.get("PYMICRO_STATSD")

    return conf


# get server setting
def get_server():
    return parse_url(get_config()["server"]["pymicro"])

def get_send_metrics():
    return get_config()["statsd"]["send_metrics"]

def get_statsd_server():
    return parse_url(get_config()["statsd"]["pymicro_statsd"])

def get_server_config():
    SERVER = get_server()
    STATSD_SERVER = get_statsd_server()
    print("PYMICRO={s}".format(s=SERVER.geturl()))
    print("PYMICRO_HOST={s}".format(s=SERVER.hostname))
    print("PYMICRO_PORT={s}".format(s=SERVER.port))
    print("PYMICRO_SEND_METRICS={s}".format(s=str(get_send_metrics()).lower()))
    print("PYMICRO_STATSD={s}".format(s=STATSD_SERVER.geturl()))
    print("PYMICRO_STATSD_HOST={s}".format(s=STATSD_SERVER.hostname))
    print("PYMICRO_STATSD_PORT={s}".format(s=STATSD_SERVER.port))
