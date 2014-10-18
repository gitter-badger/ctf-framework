import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def env_exists(config):
    return os.path.exists(os.path.join([
                                    config['database_path'],
                                    config['score_database']
    ]))

def env_init(config):
    engine = create_engine(os.path.join([config['database_path'],
                                         config['score_database']]),
                           convert_unicode=True)

    db_session = scoped_session(sessionmaker(
                                             autocommit=False,
                                             autoflush=False,
                                             bind=engine
                                            ))
    Base = declarative_base()
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
