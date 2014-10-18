#!/usr/bin/env python

import json
import os.path
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, session, \
    redirect, url_for

from view import view_blueprint
from controller import initialize_enviroment


app = Flask(__name__)

with open('config/app_config.json', 'r') as json_data:
    config = json.load(json_data)

with open('config/secret_config.json', 'r') as json_data:
    secret_config = json.load(json_data)

if __name__ == '__main__':
    handler = RotatingFileHandler(config['error-log'], maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)
    app.secret_key = secret_config['secret_key']
    app.register_blueprint(view_blueprint)
    app.run(host=config['host'], port=config['port'])

