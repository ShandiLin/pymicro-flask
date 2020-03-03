from __future__ import unicode_literals

import errno
import os
import pytest

from pymicro_flask.config import get_config, get_server_config, \
        pymicroConfigError, is_permission_denied, BaseConfigParser

DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data/conf")


class TestBaseConfigParser:
    def test_read(self):
        conf_fpath = os.path.join(DATA_DIR, "valid_conf.toml")
        bcp = BaseConfigParser(conf_fpath)
        conf = bcp.read()
        assert conf.get("title") == "Default Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']


class TestGlobalConfigParser:
    '''
        test for the config check in _preprocess function
    '''
    def test_default_config(self):
        conf = get_config()
        assert conf.get("title") == "Default Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']
        assert os.environ.get("PYMICRO_DATADIR") == "/tmp/test"

        del os.environ["PYMICRO_DATADIR"]
        conf = get_config()
        assert os.environ.get("PYMICRO_DATADIR") == "/tmp"
        os.environ["PYMICRO_DATADIR"] = "/tmp/test"

    def test_get_config(self):
        os.environ["PYMICRO"] = "http://127.0.0.1:1234"
        conf_fpath = os.path.join(DATA_DIR, "valid_conf.toml")
        conf = get_config(conf_fpath)
        assert conf["server"]["pymicro"] == "http://127.0.0.1:1234"
        del os.environ["PYMICRO"]

        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:1234"
        conf_fpath = os.path.join(DATA_DIR, "valid_conf.toml")
        conf = get_config(conf_fpath)
        assert conf["statsd"]["pymicro_statsd"] == "http://127.0.0.1:1234"
        del os.environ["PYMICRO_STATSD"]

    def test_valid_config(self):
        conf_fpath = os.path.join(DATA_DIR, "valid_conf.toml")
        conf = get_config(conf_fpath)
        assert conf.get("title") == "Default Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']

    def test_invalid_toml_format_config(self):
        conf_fpath = os.path.join(DATA_DIR, "invalid_toml.toml")
        with pytest.raises(Exception) as e:
            conf = get_config(conf_fpath)

    def test_invalid_type(self):
        for f in ["invalid_output_env_dirpath.toml",
                  "invalid_output.toml",
                  "invalid_server.toml",
                  "invalid_send_metric.toml",
                  "invalid_conf.toml"]:
            conf_fpath = os.path.join(DATA_DIR, f)
            with pytest.raises(pymicroConfigError) as e:
                conf = get_config(conf_fpath)

    def test_get_server_config(self, capsys):
        if os.environ.get("PYMICRO_SEND_METRICS"):
            del os.environ["PYMICRO_SEND_METRICS"]
        get_server_config()
        captured = capsys.readouterr()
        assert captured.out == (
            "PYMICRO=http://0.0.0.0:8080\n"
            "PYMICRO_HOST=0.0.0.0\n"
            "PYMICRO_PORT=8080\n"
            "PYMICRO_SEND_METRICS=false\n"
            "PYMICRO_STATSD=http://0.0.0.0:9125\n"
            "PYMICRO_STATSD_HOST=0.0.0.0\n"
            "PYMICRO_STATSD_PORT=9125\n"
        )

    def test_get_server_config_change_env(self, capsys):
        os.environ["PYMICRO_SEND_METRICS"] = "True"
        get_server_config()
        captured = capsys.readouterr()
        assert captured.out == (
            "PYMICRO=http://0.0.0.0:8080\n"
            "PYMICRO_HOST=0.0.0.0\n"
            "PYMICRO_PORT=8080\n"
            "PYMICRO_SEND_METRICS=true\n"
            "PYMICRO_STATSD=http://0.0.0.0:9125\n"
            "PYMICRO_STATSD_HOST=0.0.0.0\n"
            "PYMICRO_STATSD_PORT=9125\n"
        )

    def test_server_and_metric_config(self):
        os.environ["PYMICRO"] = "http://127.0.0.1:5000"
        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:8125"
        os.environ["PYMICRO_SEND_METRICS"] = "False"
        from pymicro_flask.config import get_server, get_statsd_server, get_send_metrics
        assert get_server().geturl() == "http://127.0.0.1:5000"
        assert get_statsd_server().geturl() == "http://127.0.0.1:8125"
        assert get_send_metrics() == False

        # test invalid url, it will use the default
        os.environ["PYMICRO"] = "http://:5000"
        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:abc"
        os.environ["PYMICRO_SEND_METRICS"] = "123"
        from pymicro_flask.config import get_server, get_statsd_server, get_send_metrics
        assert get_server().geturl() == "http://0.0.0.0:8080"
        assert get_statsd_server().geturl() == "http://0.0.0.0:9125"
        assert get_send_metrics() == False

    def test_is_permission_denied(self, mocker):
        assert is_permission_denied(DATA_DIR) is False
        assert is_permission_denied(
            os.path.join(os.environ["PYMICRO_DATADIR"],
                'pymicro-test-tmp')) is False

        # do not need to check when dir exists, return false
        mocker.patch('os.path.exists', return_value=False)
        mocker.patch('os.makedirs', side_effect=OSError(errno.EEXIST, "msg"))
        assert is_permission_denied(DATA_DIR) is False

        # other exception should return true
        mocker.patch('os.makedirs', side_effect=OSError)
        assert is_permission_denied(DATA_DIR) is True
