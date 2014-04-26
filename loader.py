#!/usr/bin/python2 

import os

def load_task_types():
    print "called"
    return filter(os.path.isdir, os.listdir("./tasks/" ))
