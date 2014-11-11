import os.path

from sqlalchemy import create_engine
from flask import Flask

from model import Task, Flag, Base

def env_init(config):
    path = config.get('scheme') + os.path.join(
                                    config.get('database_path'),
                                    config.get('score_database'),
    )

    engine = establish_connection(path)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine

def establish_connection(path):
    engine = create_engine(path)
    return engine

def insert_flag(connection, result, flag, task_id, teamname):
    transmission = connection.begin()
    query = Flag.insert().values(result=result,
                                 flag=flag,
                                 task_id=task_id,
                                 teamname=teamname)
    connection.execute(query)
    transmission.commit()
    connection.close()
    if result == 'fail':
        return 202
    elif result == 'already_submitted':
        return 303
    return 101
