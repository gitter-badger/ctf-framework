#!/usr/bin/python2

import os
import sys
import time
import hints
import loader
import config
import logging
import hashlib
import secretConfig

import sqlite3 as sql

from snippets import *

from flask import Flask, request, session, \
    g, redirect, url_for, abort, \
    render_template, flash

from urlparse import urlparse, parse_qs
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

ttypes = loader.load_task_types()
subttypes = loader.load_task_subtypes(ttypes)
cache = loader.load_file_cache(ttypes, subttypes)

def not_base_mod (module):
    if (module in config.base_modules):
        return False
    return True

def ftitle(var_title):
    return {
        'HOME': ('active', '', ''),
        'TASKS': ('', 'active', ''),
        'SCOREBOARD': ('', '', 'active'),
    }[var_title]

def fhead(var_title):
    return ''.join([head, (menu % ftitle(var_title)), (title % var_title)])

def fhints():
    if (not config.hints_enabled):
        return hints_disabled

    rhint = hint_top

    if (config.hints_enabled) :
        reload(hints)
        for var_hint in filter(not_base_mod,  dir(hints)):
            rhint += (snipp_hint % hints.rglobals()[var_hint])
    return rhint + hint_bottom

def fnotice (notice):
    return {
        'success': flag_added,
        'fail': flag_declined,
        'already_added': flag_already_been_added,
        '' : ''
    }[notice]

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


@app.route('/task/<task_type>/<int:cost>', methods=['GET', 'POST'])
def task(task_type, cost):
    if request.method == 'POST':
        return commit_flag(task_type, cost)
    elif request.method == 'GET':
        return show_task(task_type, cost)

def commit_flag(task_type, cost):
    if (not config.tasks_enabled):
        return 'You are trying to submit flag after CTF is over. The incedent will be reported!'

    with open ('/'. join(['tasks/', task_type, str(cost), 'desc']), 'r') as f:
        o = f.readlines()

        team_name = request.form['team_name']
        flag = hashlib.new('md5')
        flag.update(request.form['flag'])

        connection = sql.connect('score.db')
        q = "select team_name from score where task_type = ? and cost = ? and team_name = ?;"
        res = [r for r in connection.execute(q, [task_type, cost, team_name])]

        if res:
                return show_task(task_type, cost, notice='already_added')
        else:
            if(o[3].strip('\n') == flag.hexdigest()):
                q = 'insert into score values (?, ?, ?, ?);'
                connection.execute(q, [team_name,
                    task_type,
                    cost,
                    time.strftime('%Y-%m-%d %H:%M:%S')]
                )
                connection.commit()
                connection.close()

                session['team_name'] = team_name
                return show_task(task_type, cost, notice='success')

            else:
                connection.close()
                return show_task(task_type, cost, notice='fail')

def show_task(task_type, cost, notice=''):
    try:
        filename = cache[task_type][str(cost)]['filename']
    except:
        cache[task_type] = loader.load_one_file_to_cache(task_type, str(cost))

    filename = cache[task_type][str(cost)]['filename']
    taskname = cache[task_type][str(cost)]['taskname']
    description = cache[task_type][str(cost)]['description']
    flag = cache[task_type][str(cost)]['flag']

    return ''.join([fhead('TASKS'),
                        submit_bar,
                        fnotice(notice),
                        task_description.format( filename,
                            taskname,
                            description,
                            config.host_ip,
                            config.tasks_port,
                            '/'.join([task_type, str(cost)]))]
                    )

@app.route('/tasks')
def tasks():
    if (not config.tasks_enabled):
        return 'ARGHHHHHH..... Tasks are closed.'

    document = fhead('TASKS') + fhints()

    connection = sql.connect('score.db')
    q = "select * from score;"
    res = [r for r in connection.execute(q)]

    for ttype in cache.keys():
        document += (task_row_h % ttype)
        for subttype in cache[ttype]:
                    btn_style = 'btn-primary'
                    for each in res:
                        if (session.has_key('team_name') and session['team_name'] == each[0]
                            and ttype == each[1] and subttype == str(each[2])):
                            btn_style = 'btn-success'

                        elif (ttype == each[1] and subttype == str(each[2])):
                            btn_style = 'btn-warning'

                    document += (task_div.format(
                                    ttype,
                                    subttype,
                                    btn_style,
                                    cache[ttype][subttype]['taskname']
                                    )
                                )
        document += task_row_f

    connection.close()
    return document + div_row_e + footer





@app.route('/admin')
def admin():
    if (session.has_key('admin_token') and session['admin_token'] == secretConfig.secret_key):
        return admin_panel()
    else:
        return admin_log_in()

def admin_log_in (methods=['GET', 'POST']):
    if request.method == 'GET':
        login_page()
    elif request.method == 'POST':
        login_handler()

def login_handler():
    return ''

def login_page():
    return head + login_page + footer 

@app.route('/')
@app.route('/index')
def index():
    return fhead('HOME') + home + footer

if __name__ == '__main__':
    handler = RotatingFileHandler(config.errorlog, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)  
    app.logger.addHandler(handler)
    app.secret_key = secretConfig.secret_key
    app.run(host=config.host, port=config.port)
