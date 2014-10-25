import os.path
from datetime import datetime

from flask import current_app as app
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import or_, desc

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
    return session.query(Task).order_by(Task.tasktype)

def get_task_info(id):
    session = app.config.get('session')
    return session.query(Task).filter_by(id=id).first()

def get_hints(tid):
    session = app.config.get('session')
    hints = session.query(Hint).\
        filter(or_(Hint.task_id == 0, Hint.task_id == tid)).all()
    return hints

def is_flag_valid(args, addr):
    if args.has_key('teamname') and args['teamname'] and \
            args.has_key('flag') and args.has_key('task_id') and \
            args['flag'] and args['task_id']:
        engine = app.config['engine']
        teamname = sanitize_html_context(args.get('teamname'))
        task_id = sanitize_html_context(args.get('task_id'))
        flag = sanitize_html_context(args.get('flag'))

        return get_status_code(teamname, task_id, flag, addr)
    return 202

def get_status_code(teamname, task_id, flag, ip_addr):
    session = app.config.get('session')
    cost_query = session.query(Task.cost).filter_by(id=task_id).first()

    already_submitted = session.query(Flag).filter_by(
                                        teamname=teamname,
                                        task_id=int(task_id),
                                        result='success').all()

    if check_already_submitted(flag, task_id, teamname, cost_query[0], ip_addr):
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
                    cost=cost_query[0],
                    ip_addr=ip_addr,
                    datetime=datetime.now())
        session.add(success_flag)
        session.commit()
        return 101
    else:
        fail_flag = Flag(result='fail',
                    flag=flag,
                    task_id=int(task_id),
                    teamname=teamname,
                    cost=cost_query[0],
                    ip_addr=ip_addr,
                    datetime=datetime.now())
        session.add(fail_flag)
        session.commit()
        return 202

def check_already_submitted(flag, task_id, teamname, cost, ip_addr):
    session = app.config.get('session')
    already_submitted = session.query(Flag).filter_by(
                                        teamname=teamname,
                                        task_id=int(task_id),
                                        result='success').all()

    if already_submitted:
        already_flag = Flag(result='already_submitted',
                    flag=flag,
                    task_id=task_id,
                    teamname=teamname,
                    cost=cost,
                    ip_addr=ip_addr,
                    datetime=datetime.now())
        session.add(already_flag)
        session.commit()
        return True
    return False

def get_scoreboard():
    session = app.config.get('session')
    stat = session.query(
                func.sum(Flag.cost),
                Flag.teamname,
    ).filter_by(result='success').group_by(Flag.teamname).\
        order_by(desc(func.sum(Flag.cost))).\
        order_by(Flag.datetime).all()
    return stat

def get_teamdata(teamname):
    session = app.config.get('session')
    return session.query(Flag).filter_by(teamname=teamname).\
                                        order_by(Flag.datetime).all()

def proceed_teamdata(teamdata):
    success_flags = [flag.cost for flag in teamdata if flag.result == 'success']
    commits = len(teamdata)
    solved = len(success_flags)
    pts = sum(success_flags)
    last_commit = teamdata.pop().datetime
    return pts, solved, commits, last_commit

def get_commits():
    session = app.config.get('session')
    commits = session.query(Flag).all()
    return commits

def get_solved_tasks(teamname):
    session = app.config.get('session')
    solved_tasks = session.query(Flag.task_id).\
        filter_by(teamname=teamname, result='success').all()
    return solved_tasks

def get_taskname_by_id(task_id):
    session = app.config.get('session')
    return session.query(Task.taskname).\
        filter_by(id=task_id).first()
