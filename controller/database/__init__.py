import os.path

from sqlalchemy import create_engine
from flask import Flask

from model import Task, Flag, metadata

def env_init(config):
    engine = create_engine(config.get('scheme') + os.path.join(
                                    config.get('database_path'),
                                    config.get('score_database'),
    ))
    metadata.create_all(engine, checkfirst=True)
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
