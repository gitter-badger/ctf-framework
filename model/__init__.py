
from sqlalchemy import Table, Column, MetaData, text
from sqlalchemy import Integer, String, DateTime


metadata = MetaData()

Task = Table('tasks', metadata,
    Column('id', Integer, primary_key=True),
    Column('taskname', String(40), unique=True),
    Column('flag', String(80), unique=True),
    Column('cost', Integer),
    Column('description', String(1024))
)

Flag = Table('flag', metadata,
    Column('id', Integer, primary_key=True),
    Column('result', String(15)),
    Column('taskname', String(40)),
    Column('teamname', String(40)),
)


