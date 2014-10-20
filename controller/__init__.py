import os.path

from flask import current_app as app
from sqlalchemy.orm import sessionmaker

import database
from model import Task, Flag


def initialize_enviroment(config):
    ''' Initializes the databases if they do not exist
    and tables in them '''
    return database.env_init(config)

def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    session._model_changes = {}
    return session

def get_tasks(config):
    session = config.get('session')
    return session.query(Task).order_by("tasktype")

def get_task_info():
    pass
