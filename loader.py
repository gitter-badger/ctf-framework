#!/usr/bin/python2 

import os

def load_task_types():
    return [item for item in os.listdir('tasks') if os.path.isdir('tasks' '/' + item)]

def load_task_subtypes(ttypes):
    r = {}
    for ttype in ttypes: 
        r[ttype] = [item for item in os.listdir('tasks' '/' + ttype) if os.path.isdir( '/'.join(['tasks', ttype,  item]))]
    return r

def load_file_cache(ttypes, subttypes):
    cache = { } 
    for ttype in subttypes.keys():
        for subttype in subttypes[ttype]:
            try:
                with open ('/'.join(['tasks', ttype, subttype, 'desc'])) as f:
                    cache[ttype] = { }
                    cache[ttype][subttype] = {'filename': f.readline().strip('\n'), 'taskname': f.readline().strip('\n'),
                                        'description': f.readline().strip('\n'), 'flag': f.readline().strip('\n')
                                    }
            except IOError:
                pass
    return cache