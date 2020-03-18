# -*- coding: utf-8 -*-
import errno
import os
import pytest

from pymicro_flask.config.parser import BaseConfigParser, DefaultConfigParser, \
        PymicroConfigError, is_permission_denied


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_data/conf")


class TestBaseConfigParser:
    def test_read(self):
        bcp = BaseConfigParser(os.environ["PYMICRO_CONFIG"])
        conf = bcp.read()
        assert conf.get("title") == "Test Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']


class TestDefaultConfigParser:
    '''
        test for the config check in _preprocess function
    '''
    def test_read(self):
        dcp = DefaultConfigParser(os.environ["PYMICRO_CONFIG"])
        conf = dcp.read()
        assert conf.get("title") == "Test Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']

    def test_invalid_toml_format_config(self):
        conf_fpath = os.path.join(DATA_DIR, "invalid", "invalid_toml.toml")
        with pytest.raises(Exception) as e:
            dcp = DefaultConfigParser(conf_fpath)
            conf = dcp.read()

    def test_invalid_type(self):
        for f in ["invalid_output_env_dirpath.toml",
                  "invalid_output.toml",
                  "invalid_server.toml",
                  "invalid_send_metric.toml",
                  "invalid_conf.toml"]:
            conf_fpath = os.path.join(DATA_DIR, "invalid", f)
            with pytest.raises(PymicroConfigError) as e:
                dcp = DefaultConfigParser(conf_fpath)
                conf = dcp.read()

    def test_is_permission_denied(self, mocker):
        assert is_permission_denied(DATA_DIR) is False
        assert is_permission_denied(os.path.join(
            os.environ["PYMICRO_DATADIR"], 'pymicro-test-tmp'
        )) is False

        # do not need to check when dir exists, return false
        mocker.patch('os.path.exists', return_value=False)
        mocker.patch('os.makedirs', side_effect=OSError(errno.EEXIST, "msg"))
        assert is_permission_denied(DATA_DIR) is False

        # other exception should return true
        mocker.patch('os.makedirs', side_effect=OSError)
        assert is_permission_denied(DATA_DIR) is True
