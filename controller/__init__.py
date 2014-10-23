import os.path

from flask import current_app as app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

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

def get_tasks():
    session = app.config.get('session')
    return session.query(Task).order_by("tasktype")

def get_task_info(id):
    session = app.config.get('session')
    return session.query(Task).filter_by(id=id).first()

def is_flag_valid(args):
    if args.has_key('teamname') and args['teamname'] and \
            args.has_key('flag') and args.has_key('task_id'): #and \
        engine = app.config['engine']

    status_code = get_status_code(args.get('teamname'),
                                    args.get('task_id'),
                                    args.get('flag')
                                    )
    return status_code

def get_status_code(teamname, task_id, flag):
    session = app.config.get('session')
    already_submitted = session.query(Flag).filter_by(
                                        teamname=teamname,
                                        task_id=task_id,
                                        result='success').all()
    if already_submitted:
         return database.insert_flag(connection=app.config['engine'].connect(),
                    result='already_submitted',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname)
    flag_query = session.query(Task).filter_by(id=task_id,
                                        flag=flag).all()
    if flag_query:
        return database.insert_flag(connection=app.config['engine'].connect(),
                    result='success',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname)
    else:
        return database.insert_flag(connection=app.config['engine'].connect(),
                    result='fail',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname)


