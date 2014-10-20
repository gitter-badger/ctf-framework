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

