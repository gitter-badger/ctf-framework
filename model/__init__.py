from sqlalchemy import Table, Column, MetaData
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Task(Base):
    __tablename__  = 'tasks'
    id = Column('id', Integer, primary_key=True)
    taskname = Column('taskname', String(40), unique=True)
    flag = Column('flag', String(80), unique=True)
    tasktype = Column('tasktype', String(15))
    cost = Column('cost', Integer)
    description = Column('description', String(1024))
    enabled = Column('enabled', Integer)

class Flag(Base):
    __tablename__ = 'flags'
    id = Column('id', Integer, primary_key=True)
    task_id = Column('task_id', Integer)
    teamname = Column('teamname', String(40))
    flag = Column('flag', String(80))
    cost = Column('cost', Integer)
    result = Column('result', String(15))
    ip_addr = Column('ip_addr', String(20))
    datetime = Column("commitdate", DateTime())

class Hint(Base):
    __tablename__ = 'hints'
    id = Column('id', Integer, primary_key=True)
    task_id = Column('task_id', Integer)
    hint = Column('hint', String(512))


