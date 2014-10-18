
import os.path

import database

def initialize_enviroment(config):
    ''' Initializes the databases if they do not exist
    and tables in them '''
    if not database.env_exists(config):
        return database.env_init(config)
