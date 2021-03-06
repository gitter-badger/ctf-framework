#!/usr/bin/env python

import sys
import json
import os.path
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, session, redirect, url_for

from view import view_blueprint
from controller import initialize_enviroment, create_session, parse_argv
from controller import initialize_results, init_countdown

app = Flask(__name__)

with open('config/app_config.json', 'r') as json_data:
    config = json.load(json_data)

with open('config/secret_config.json', 'r') as json_data:
    secret_config = json.load(json_data)

with open('config/results.json', 'r') as json_data:
    result_config = json.load(json_data)

if __name__ == '__main__':
    # Setting up loggers
    handler = RotatingFileHandler(config['error-log'],
        maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # App Initialization
    app.config = dict(app.config, **config)
    app.config['results'] = result_config
    args = vars(parse_argv())
    init_countdown(app.config)

    # Setting up database
    app.config['engine'] = initialize_enviroment(app.config)
    app.config['session'] = create_session(app.config['engine'])
    app.config['result_engines'] = initialize_results()

    # Security settings
    app.secret_key = secret_config['secret_key']
    app.config['admin_token'] = secret_config['admin_token']

    # Running the app
    app.register_blueprint(view_blueprint)
    app.run(host=config['host'], port=args['port'].pop())

