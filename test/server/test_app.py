from __future__ import unicode_literals

from pymicro_flask.server.app import create_app, api


def test_create_app():
    app = create_app()
    pymicro_flask_api = api.resources[0]
    assert pymicro_flask_api[1][0] == '/microservice'
    assert pymicro_flask_api[0].__name__ == "MsgProcess"
