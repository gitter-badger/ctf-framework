
from sqlalchemy import Table, Column, MetaData
from sqlalchemy import Integer, String, DateTime


metadata = MetaData()

Task = Table('tasks', metadata,
    Column('id', Integer, primary_key=True),
    Column('taskname', String(40), unique=True),
    Column('flag', String(80), unique=True),
    Column('tasktype', String(15)),
    Column('cost', Integer),
    Column('description', String(1024)),
    Column('enabled', Integer),
)

Flag = Table('flags', metadata,
    Column('id', Integer, primary_key=True),
    Column('result', String(15)),
    Column('flag', String(80)),
    Column('task_id', Integer),
    Column('teamname', String(40)),
)

Hint = Table('hints', metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer),
    Column('hint', String(512)),
)


