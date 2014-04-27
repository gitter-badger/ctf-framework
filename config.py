# Config file for this amazing system

import sys

host = "0.0.0.0" # broadcast range
host_ip = "10.0.0.1" # ip_addr of interface you are currently using
port = 8088
tasks_port = 8888

sys.dont_write_bytecode = True

tasks_enabled = 1
scoreboard_enabled = 1
hints_enabled = 1

base_modules = ['__builtins__', '__doc__', '__file__', '__name__', '__package__']


accesslog = '/var/log/msuctf-access.log'
errorlog = '/var/log/msuctf-error.log'

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
 