#!/usr/bin/python2 

import os

def load_task_types():
    return [item for item in os.listdir('tasks') if os.path.isdir('tasks' '/' + item)]

def load_task_subtypes(ttypes):
	r = {}
	for ttype in ttypes: 
		r[ttype] = [item for item in os.listdir('tasks' '/' + ttype) if os.path.isdir( '/'.join(['tasks', ttype,  item]))]

	return r