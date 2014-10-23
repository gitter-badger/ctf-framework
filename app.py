#!/usr/bin/env python

import json
import os.path
import logging
from logging.handlers import RotatingFileHandler

from OpenSSL import SSL
from sqlalchemy.orm import Session, sessionmaker
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
    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('yourserver.crt', 'yourserver.key')

    # Running the app
    app.register_blueprint(view_blueprint)
    app.run(host=config['host'], port=config['port']) # , ssl_context=context)

