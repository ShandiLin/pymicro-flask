# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api

from pymicro_flask.server.resouces import MsgProcess


api = Api()
api.add_resource(MsgProcess, '/microservice')


def create_app():
    app = Flask(__name__)
    api.init_app(app)
    return app
