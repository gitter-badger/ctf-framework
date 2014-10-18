
from functools import wraps
import os.path

import database


def initialize_enviroment(config):
    ''' Initializes the databases if they do not exist
    and tables in them '''
    if database.env_exists(config):
        database.env_init(config)
