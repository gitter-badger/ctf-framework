import argparse
import os.path
import sched
import time
from threading import Timer
from datetime import datetime

from flask import current_app as app
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import or_, desc, distinct

import database
from model import Task, Flag, Hint


def initialize_enviroment(config):
    ''' Initializes the databases if they do not exist
    and tables in them '''
    return database.env_init(config)

def initialize_results():
    result = []

def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def parse_argv():
    parser = argparse.ArgumentParser(description='CTF-Framework')
    parser.add_argument('port', nargs=1, type=int, help='a port to start with')
    return parser.parse_args()

def get_tasks():
    session = app.config.get('session')
    return session.query(Task).order_by(Task.tasktype).order_by(Task.cost)

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
        teamname = args.get('teamname')
        task_id = args.get('task_id')
        flag = args.get('flag')

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

def get_result_list():
    result = app.config.get('results')
    return result

def get_scoreboard():
    session = app.config.get('session')
    stat = session.query(
                func.sum(Flag.cost),
                Flag.teamname,
    ).filter_by(result='success').group_by(Flag.teamname).\
        order_by(desc(func.sum(Flag.cost))).\
        order_by(Flag.datetime).all()
    return stat

def get_teamdata(teamname, session=None):
    if session is None:
        session = app.config.get('session')
    return session.query(Flag).filter_by(teamname=teamname).\
                                        order_by(Flag.datetime).all()

def proceed_teamdata(teamdata):
    success_flags = [flag.cost for flag in teamdata if flag.result == 'success']
    solved = len(success_flags)
    pts = sum(success_flags)
    last_commit = teamdata.pop().datetime
    return pts, solved, last_commit

def get_commits():
    session = app.config.get('session')
    commits = session.query(Flag).all()
    return commits

def get_solved_tasks(teamname, session=None):
    if session is None:
        session = app.config.get('session')
    solved_tasks = session.query(Flag.task_id).\
        filter_by(teamname=teamname, result='success').all()
    return solved_tasks

def get_tasknametype_by_id(task_id, session=None):
    if session is None:
        session = app.config.get('session')
    return session.query(Task.taskname, Task.tasktype).\
        filter_by(id=task_id).first()

def get_less_results(session):
    stat = session.query(
                func.sum(Flag.cost),
                Flag.teamname,
    ).filter_by(result='success').group_by(Flag.teamname).\
        order_by(desc(func.sum(Flag.cost))).\
        order_by(Flag.datetime).all()
    return stat

def get_global_stats(session):
    total_tasks = session.query(func.count(Task.id)).first()
    total_commits = session.query(func.max(Flag.id)).first()
    total_valid_commits = session.query(func.count(Flag.id)).\
        filter_by(result='success').first()
    total_teams = session.query(func.count(distinct(Flag.teamname))).first()
    stats = session.query(func.count(Flag.id), Task.taskname).\
        filter_by(result='success').\
        join(Task, Task.id == Flag.task_id).\
        group_by(Task.id).order_by(func.count(Flag.id)).all()
    total_tasks_solved = (len(stats),)

    return total_tasks, total_tasks_solved, total_commits, total_valid_commits, \
        total_teams, stats

def edit_settings(settings):
    if settings.get('tasks'):
        app.config['tasks_opened'] ^= True
    if settings.get('scoreboard'):
        app.config['scoreboard_opened'] ^= True
    if settings.get('results'):
        app.config['results_opened'] ^= True
    if settings.get('freeze'):
        app.config['scoreboard_frozen'] ^= True

def init_countdown(config):
    freeze = int(config['scoreboard_freeze'])
    start_time = int(config['start_time'])
    length = int(config['end_time']) - start_time
    passed_time = int(time.time()) - start_time

    settings = {
                'tasks': True,
                'scoreboard': True,
    }

    if passed_time > length:
        return False

    if passed_time < 0:
        Timer(-passed_time, edit_settings, settings).start()
    if passed_time < freeze:
        Timer(-passed_time + freeze, edit_settings, {'scoreboard': True}).start()
    if passed_time < length:
        Timer(-passed_time + length, edit_settings, {'tasks': True}).start()
    return passed_time





