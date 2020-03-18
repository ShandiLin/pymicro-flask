# -*- coding: utf-8 -*-
import errno
import os
import shutil
import six
import toml
import traceback

from pymicro_flask.utils import is_valid_url


class BaseConfigParser(object):
    ''' Base class to read .toml file config. Override this class and define value checking in _preprocess
        All the common check functions should be defined here.
        Param:
            conf_path(str): config file path
        Usage:
            bcp = BaseConfigParser(conf_path)
            conf = bcp.read()
    '''
    def __init__(self, conf_path):
        self.conf_path = conf_path

    def _preprocess(self, conf_obj):
        # validate setting
        pass

    def _check_string(self, key, val):
        if not isinstance(val, six.string_types):
            raise PymicroConfigError(
                "'{k}' should be defined and type of value should be string." \
                    .format(k=key)
            )

    def _check_bool(self, key, val):
        if not isinstance(val, bool):
            raise PymicroConfigError(
                "'{k}' should be defined and type of value should be boolean." \
                    .format(k=key)
            )

    def _check_section_exist(self, conf, key, sub_keys):
        if conf.get(key) is None:
            raise PymicroConfigError(
                "'{k}' should be set as section and contains key_list {ks}." \
                    .format(k=key, ks=sub_keys)
            )
        return conf.get(key)

    def _check_valid_url(self, key, val):
        if is_valid_url(val) is False:
            raise PymicroConfigError(
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


class DefaultConfigParser(BaseConfigParser):
    ''' Read and check global pymicro service config.
        In _preprocess function, it will check keys in section and value types.
        It also get real path in 'output' section by invoking expandvars.
        Param:
            conf_path(str): config file path
        Usage:
            gcp = GlobalConfigParser(conf_path)
            conf = gcp.read()
    '''
    def __init__(self, conf_path):
        super(DefaultConfigParser, self).__init__(conf_path)

    def _preprocess(self, conf_obj):
        try:
            # check server
            server_sec = self._check_section_exist(conf_obj, "server", ["pymicro_server"])
            self._check_string("pymicro_server", server_sec.get("pymicro_server"))
            self._check_valid_url("pymicro_server", server_sec.get("pymicro_server"))

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
                    raise PymicroConfigError("check config value of " + k)
            if is_permission_denied(conf_obj["output"]["data_dir"]) is True:
                raise PymicroConfigError("can not create folder for data in path: " + conf_obj["output"]["pdf_dir"])
        except PymicroConfigError as e:
            raise


class PymicroConfigError(Exception):
    pass


def is_permission_denied(fpath):
    ''' try to create folders from fpath, return True if it failed '''
    if not os.path.exists(fpath):
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
