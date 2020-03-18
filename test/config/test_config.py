# -*- coding: utf-8 -*-
import errno
import os
import pytest

from pymicro_flask.config.config import DefaultConfig, PymicroConfig
from pymicro_flask.config.parser import PymicroConfigError


DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "test_data/conf")


class TestDefaultConfig:
    '''
        test for pymicro default config
    '''
    def test_default_config(self):
        default_conf = DefaultConfig()
        conf = default_conf.conf
        assert conf.get("title") == "Default Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']

    def test_print_server_config(self, capsys):
        if os.environ.get("PYMICRO_SEND_METRICS"):
            del os.environ["PYMICRO_SEND_METRICS"]
        default_conf = DefaultConfig()
        default_conf.print_server_config()
        captured = capsys.readouterr()
        assert captured.out == (
            "PYMICRO_SERVER=http://0.0.0.0:8080\n"
            "PYMICRO_HOST=0.0.0.0\n"
            "PYMICRO_PORT=8080\n"
            "PYMICRO_SEND_METRICS=false\n"
            "PYMICRO_STATSD=http://0.0.0.0:9125\n"
            "PYMICRO_STATSD_HOST=0.0.0.0\n"
            "PYMICRO_STATSD_PORT=9125\n"
        )


class TestPymicroConfig:
    '''
        test for pymicro config that some values would be overwrite by env vars
    '''
    def test_pymicro_config_using_default(self):
        test_pymicro_conf = os.environ["PYMICRO_CONFIG"]
        del os.environ["PYMICRO_CONFIG"]
        pymicro_conf = PymicroConfig()
        conf = pymicro_conf.conf
        assert conf.get("title") == "Default Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']
        os.environ["PYMICRO_CONFIG"] = test_pymicro_conf

    def test_pymicro_config_using_env_vars(self):
        pymicro_conf = PymicroConfig()
        conf = pymicro_conf.conf
        assert conf.get("title") == "Test Service Config"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']

    def test_pymicro_config_using_param_conf(self):
        pymicro_conf = PymicroConfig(os.path.join(DATA_DIR, "test_config1.toml"))
        conf = pymicro_conf.conf
        assert conf.get("title") == "Test Service Config - 1"
        assert sorted(conf.keys()) == ['output', 'server', 'statsd', 'title']

    def test_pymicro_config_overwrite_by_env_vars(self):
        os.environ["PYMICRO_SERVER"] = "http://127.0.0.1:1234"
        pymicro_conf = PymicroConfig()
        assert pymicro_conf.conf["server"]["pymicro_server"] == "http://127.0.0.1:1234"
        del os.environ["PYMICRO_SERVER"]

        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:1234"
        pymicro_conf = PymicroConfig()
        assert pymicro_conf.conf["statsd"]["pymicro_statsd"] == "http://127.0.0.1:1234"
        del os.environ["PYMICRO_STATSD"]

    def test_print_server_config_change_env(self, capsys):
        os.environ["PYMICRO_SEND_METRICS"] = "True"
        pymicro_conf = PymicroConfig()
        pymicro_conf.print_server_config()
        captured = capsys.readouterr()
        assert captured.out == (
            "PYMICRO_SERVER=http://0.0.0.0:8080\n"
            "PYMICRO_HOST=0.0.0.0\n"
            "PYMICRO_PORT=8080\n"
            "PYMICRO_SEND_METRICS=true\n"
            "PYMICRO_STATSD=http://0.0.0.0:9125\n"
            "PYMICRO_STATSD_HOST=0.0.0.0\n"
            "PYMICRO_STATSD_PORT=9125\n"
        )

    def test_server_and_metric_config(self):
        os.environ["PYMICRO_SERVER"] = "http://127.0.0.1:5000"
        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:8125"
        os.environ["PYMICRO_SEND_METRICS"] = "True"
        pymicro_conf = PymicroConfig()
        assert pymicro_conf.get_server().geturl() == "http://127.0.0.1:5000"
        assert pymicro_conf.get_statsd_server().geturl() == "http://127.0.0.1:8125"
        assert pymicro_conf.get_send_metrics() == True

        # test invalid url or boolean, it will use the default value
        os.environ["PYMICRO_SERVER"] = "http://:5000"
        with pytest.warns(UserWarning):
            pymicro_conf = PymicroConfig()
            assert pymicro_conf.get_server().geturl() == "http://0.0.0.0:8080"

        os.environ["PYMICRO_STATSD"] = "http://127.0.0.1:abc"
        with pytest.warns(UserWarning):
            pymicro_conf = PymicroConfig()
            assert pymicro_conf.get_statsd_server().geturl() == "http://0.0.0.0:9125"

        os.environ["PYMICRO_SEND_METRICS"] = "123"
        with pytest.warns(UserWarning):
            pymicro_conf = PymicroConfig()
            assert pymicro_conf.get_send_metrics() == False
