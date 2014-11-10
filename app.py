#!/usr/bin/env python

import sys
import json
import os.path
import logging
from logging.handlers import RotatingFileHandler

from OpenSSL import SSL
from flask import Flask, request, session, \
    redirect, url_for

from view import view_blueprint
from controller import initialize_enviroment, create_session

app = Flask(__name__)

with open('config/app_config.json', 'r') as json_data:
    config = json.load(json_data)

with open('config/secret_config.json', 'r') as json_data:
    secret_config = json.load(json_data)

if __name__ == '__main__':
    # Setting up loggers
    handler = RotatingFileHandler(config['error-log'],
        maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    # App Initialization
    app.config = dict(app.config, **config)
    app.config['engine'] = initialize_enviroment(app.config)
    app.config['session'] = create_session(app.config['engine'])

    # Setting up database
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['scheme'] + os.path.join(
        app.config['database_path'],
        app.config['score_database'],
    )


    # Security settings
    app.secret_key = secret_config['secret_key']
    app.config['admin_token'] = secret_config['admin_token']
    context = SSL.Context(SSL.SSLv23_METHOD)

    # Running the app
    app.register_blueprint(view_blueprint)
    if len(sys.argv) == 2:
        app.run(host=config['host'], port=int(sys.argv[1])) #, ssl_context=('files/ssl/server.crt', 'files/ssl/server.key'))
    else:
        print 'need two args'
    
