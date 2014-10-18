import os.path

from sqlalchemy import create_engine

from model import Task, Flag, metadata
from view import view_blueprint as view

def env_exists(config):
    return os.path.exists(os.path.join(
                                    config['database_path'],
                                    config['score_database'],
    ))

def env_init(config):
    engine = create_engine(config['scheme'] + os.path.join(
                                    config['database_path'],
                                    config['score_database']
    ))
    metadata.create_all(engine, checkfirst=True)
    return engine
