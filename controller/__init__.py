import os.path

from flask import current_app as app
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import or_

import database
from model import Task, Flag, Hint
from security import sanitize_html_context


def initialize_enviroment(config):
    ''' Initializes the databases if they do not exist
    and tables in them '''
    return database.env_init(config)

def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_tasks():
    session = app.config.get('session')
    return session.query(Task).order_by("tasktype")

def get_task_info(id):
    session = app.config.get('session')
    return session.query(Task).filter_by(id=id).first()

def get_hints(tid):
    session = app.config.get('session')
    hints = session.query(Hint).\
        filter(or_(Hint.task_id == 0, Hint.task_id == tid)).all()
    return hints

def is_flag_valid(args):
    if args.has_key('teamname') and args['teamname'] and \
            args.has_key('flag') and args.has_key('task_id') and \
            args['flag'] and args['task_id']:
        engine = app.config['engine']
        teamname = sanitize_html_context(args.get('teamname'))
        task_id = sanitize_html_context(args.get('task_id'))
        flag = sanitize_html_context(args.get('flag'))

    status_code = get_status_code(teamname, task_id, flag)
    return status_code

def get_status_code(teamname, task_id, flag):
    session = app.config.get('session')
    cost_query = session.query(Task.cost).filter_by(id=task_id).first()

    already_submitted = session.query(Flag).filter_by(
                                        teamname=teamname,
                                        task_id=int(task_id),
                                        result='success').all()

    if check_already_submitted(flag, int(task_id), teamname, cost_query[0]):
        return 303

    flag_query = session.query(Task).filter_by(id=task_id, flag=flag).all()
    cost_query = session.query(Task.cost).filter_by(id=task_id).first()
    if not cost_query:
        return 202

    if flag_query:
        success_flag = Flag(result='success',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname,
                    cost=cost_query[0])
        session.add(success_flag)
        session.commit()
        return 101
    else:
        fail_flag = Flag(result='fail',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname,
                    cost=cost_query[0])
        session.add(fail_flag)
        session.commit()
        return 202

def check_already_submitted(flag, task_id, teamname, cost):
    session = app.config.get('session')
    already_submitted = session.query(Flag).filter_by(
                                        teamname=teamname,
                                        task_id=task_id,
                                        result='success').all()

    if already_submitted:
        already_flag = Flag(result='already_submitted',
                    flag=flag,
                    task_id=task_id,
                    teamname=teamname,
                    cost=cost)
        session.add(already_flag)
        session.commit()
        return True
    return False

def get_scoreboard():
    session = app.config.get('session')
    stat = session.query(
                func.sum(Flag.cost),
                Flag.teamname,
    ).filter_by(result='success').group_by(Flag.teamname).all()
    return stat

