#!/usr/bin/python2

import os
import sys
import time
import hints
import loader
import config
import logging

import sqlite3 as sql

from snippets import *

from flask import Flask, request, session, \
    g, redirect, url_for, abort, \
    render_template, flash

from urlparse import urlparse, parse_qs

app = Flask(__name__)

ttypes = loader.load_task_types()
subttypes = loader.load_task_subtypes(ttypes)


#
# This part is NOT FINISHED YET
# TO DEL

#     def do_POST(self):
#         if (config.tasks_enabled):
#             q = urlparse(self.path)
#             args = parse_qs(q.query)

#             length = int(self.headers.getheader('content-length'))
#             postvars = parse_qs(self.rfile.read(length))

#             if (postvars.has_key('team_name') and postvars.has_key('flag')):
#                 with open ('/'. join(['tasks/', args['t'][0],args['c'][0], 'desc']), 'r') as f:
#                     o = f.readlines()
#                     self.send_response(301)

#                     connection = sql.connect('score.db')
#                     q = "select team_name from score where flag = \'%s\' and team_name = \'%s\';"
#                     res = connection.execute(q % (postvars['flag'][0], postvars['team_name'][0]))
#                     for row in res:
#                         if (row):
#                             self.send_header('Location', 'index?r=already_added')
#                             break
#                     else:
#                         if(o[3].strip('\n') == postvars['flag'][0]):
#                             q = 'insert into score values (\'%s\', \'%s\', %s, \'%s\');'
#                             connection.execute(q % (postvars['team_name'][0],
#                                 postvars['flag'][0],
#                                 args['c'][0],
#                                 time.strftime('%Y-%m-%d %H:%M:%S'))
#                                                 )
#                             connection.commit()
                            
#                             self.send_header('Location', 'index?r=success')
#                         else:
#                             self.send_header('Location', 'index?r=fail')

#                     connection.close()

#                 self.end_headers()

#             else:
#                 self.send_response(200)
#                 self.send_header('Content-type', 'text/html')
#                 self.end_headers()
#         else:
#             document = 'You are trying to submit flag after CTF is over. The incedent will be reported!'
#             self.send_response(200)
#             self.send_header('Content-type', 'text/html')
#             self.end_headers()
#             self.wfile.write(document)

#     notice = ""

def ftitle(var_title):
    return {
        'HOME': ('active', '', ''),
        'TASKS': ('', 'active', ''),
        'SCOREBOARD': ('', '', 'active'),
    }[var_title]

def fhead(var_title):
    return '\n'.join([head, (menu % ftitle(var_title)), (title % var_title)])

def not_base_mod (module):
    if (module in config.base_modules):
        return False
    return True

def fhints():
    if (not config.hints_enabled):
        return hints_disabled

    rhint = hint_top

    if (config.hints_enabled) :
        reload(hints)
        for var_hint in filter(not_base_mod,  dir(hints)):  
            rhint += snipp_hint % hints.rglobals()[var_hint]
    return rhint + hint_bottom

@app.route('/scoreboard')
def scoreboard ():
    if (not config.scoreboard_enabled):
        return 'Karim says: \'Stop fapping on the scoreboard !\' '

    connection = sql.connect('score.db')
    q = 'select team_name, sum(cost) from score group by team_name order by sum(cost) DESC, date;'
    res = connection.execute(q)

    document = fhead('SCOREBOARD') + scoreboard_head
    j = 0
    for row in res:
        j += 1
        document += scoreboard_cell % (j, row[0], row[1])

    connection.close()
    return document + scoreboard_footer

    
@app.route('/task/<task_name>/<int:cost>')
def task(task_name, cost):
    with open ( '/'.join( ['tasks', task_name, cost, 'desc' ] ), 'r') as f:
            return '\n'.join( [head,    submit_bar,
                                menu % ('', 'active', ''), (title % task_name), 
                                task_description.format( f.readline().strip('\n'),
                                    f.readline().strip('\n'),
                                    f.readline().strip('\n'),
                                    host_ip,
                                    tasks_port,
                                    '/'.join([task_name, cost]))]
                            )

@app.route('/tasks')
def tasks():
    if (not config.tasks_enabled):
        return 'ARGHHHHHH..... Tasks are closed.'

    document = fhead('TASKS') + fhints()

    # If session isset the select * from table score
    #   
    # else do nothing 

    for ttype in ttypes:
        document += (task_row_h % ttype)
        for subttype in subttypes[ttype]:
            dp = '/'.join(['tasks', ttype, subttype, 'desc'])
            if (os.path.isfile(dp)):
                with open (dp, 'r') as f:
                    f.readline()
                    document += (task_div.format(
                                    ttype,
                                    subttype,
                                    'btn-primary',
                                    f.readline().strip('\n')
                                    )
                                )
            document += task_row_f
    return document + div_row_e + footer


@app.route('/')
@app.route('/index')
def index():
    return fhead('HOME') + home + footer

if __name__ == '__main__':
    app.run(host=config.host, port=config.port)