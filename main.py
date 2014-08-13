#!/usr/bin/python2

import os
import re
import sys
import time
import loader
import logging
import hashlib

import sqlite3 as sql

from snippets import *
from urlparse import urlparse
from logging.handlers import RotatingFileHandler

from flask import Flask, request, session, \
    g, redirect, url_for, abort

app = Flask(__name__)

ttypes = loader.load_task_types()
subttypes = loader.load_task_subtypes(ttypes)
cache = loader.load_file_cache(ttypes, subttypes)

cfg = loader.load_config()
secret_cfg = loader.load_secret_config()

def not_base_mod (module):
    return not module in cfg['base_modules']

def ftitle(var_title):
    return {
        'HOME': ('active', '', ''),
        'TASKS': ('', 'active', ''),
        'SCOREBOARD': ('', '', 'active')
    }[var_title]

def fhead(var_title):
    return ''.join([head, (menu % (ftitle(var_title))), (title.format(var_title))])

def fhints():
    if not cfg['hints_enabled']:
        return hints_disabled

    rhint = hint_top
    hints = loader.load_hints()

    for hint in hints.itervalues():
        rhint += snipp_hint.format(hint)
    return rhint + hint_bottom

def fnotice (notice):
    return {
        'success': flag_added,
        'danger': flag_declined,
        'already_added': flag_already_been_added,
        '' : ''
    }[notice]

@app.route('/scoreboard')
def scoreboard ():
    if not cfg['scoreboard_enabled']:
        return 'Karim says: \'Stop fapping on the scoreboard !\''

    connection = sql.connect('score.db')
    q = 'select team_name, sum(cost) from score group by team_name order by sum(cost) DESC, date;'
    res = connection.execute(q)

    document = fhead('SCOREBOARD') + scoreboard_head
    j = 0
    for row in res:
        j += 1
        document += scoreboard_cell.format(j, row[0], row[1])

    connection.close()
    return document + scoreboard_footer

@app.route('/task/<task_type>/<int:cost>', methods=['GET', 'POST'])
def task(task_type, cost):
    if request.method == 'POST':
        return commit_flag(task_type, cost)
    elif request.method == 'GET':
        return show_task(task_type, cost)

def commit_success(request, task_type, cost):
    connection = sql.connect('score.db')
    log = open('logs/msuctf-submit.log', 'a')
    q = 'insert into score values (?, ?, ?, ?);'
    log.write(' '.join (['success', request.form['team_name'].replace(' ', '_'), request.form['flag'].replace(' ', '_'),
        task_type + str(cost), time.strftime('%Y-%m-%d %H:%M:%S'),
        request.remote_addr, '\n']))

    connection.execute(q, [request.form['team_name'],
        task_type,
        cost,
        utime]
    )
    connection.commit()
    connection.close()

    session['team_name'] = request.form['team_name']
    log.close()

    return show_task(task_type, cost, notice='success')

def commit_already_added(request, task_type, cost):
    log = open('logs/msuctf-submit.log', 'a')
    log.write(' '.join (['warning', request.form['team_name'].replace(' ', '_'), request.form['flag'].replace(' ', '_'),
        os.path.join(task_type, str(cost)), time.strftime('%Y-%m-%d %H:%M:%S'),
        request.remote_addr, '\n' ])
    )
    log.close()
    return show_task(task_type, cost, notice='already_added')

def commit_fail(request, task_type, cost):
    log = open('logs/msuctf-submit.log', 'a')
    log.write(' '.join (['danger', request.form['team_name'].replace(' ', '_'), request.form['flag'].replace(' ', '_'),
                                task_type + '/' + str(cost), utime,
                                request.remote_addr, '\n' ]))
    log.close()
    return show_task(task_type, cost, notice='danger')

def commit_attack_attempt(request, task_type, cost):
    print "ATTACK_ATTEMPT"
    attack_log = open('logs/msuctf-attack.log','a')
    attack_log.write(' '.join ([request.form['team_name'], request.form['flag'],
                    task_type + '/' + str(cost), time.strftime('%Y-%m-%d %H:%M:%S'),
                    request.remote_addr, '\n' ]))
    attack_log.close()
    return show_task(task_type, cost, notice='danger')

def commit_flag(task_type, cost):
    if not cfg['tasks_enabled']:
        return 'You are trying to submit flag after CTF is over. The incedent will be reported!'

    with open (os.path.join('tasks/', task_type, str(cost), 'desc'), 'r') as f:
        o = f.readlines()

        flag = hashlib.new('md5')
        flag.update(request.form['flag'])

        q = "select team_name from score where task_type = ? and cost = ? and team_name = ?;"
        connection = sql.connect('score.db')
        res = [r for r in connection.execute(q, [task_type, cost, request.form['team_name']])]

        if re.match('[^\w\*]', request.form['flag']) and re.match('[^\w\*]', request.form['team_name']) :
            return commit_attack_attempt(request, task_type, cost)
        if res:
            return commit_already_added(request, task_type, cost)
        if o[3].strip('\n') == flag.hexdigest():
            return commit_success(request, task_type, cost)
        else:
            return show_task(task_type, cost, notice='danger')

def show_task(task_type, cost, notice=''):
    try:
        filename = cache[task_type][str(cost)]['filename']
    except:
        cache[task_type] = loader.load_one_file_to_cache(task_type, str(cost))

    filename = cache[task_type][str(cost)]['filename']
    taskname = cache[task_type][str(cost)]['taskname']
    description = cache[task_type][str(cost)]['description']
    flag = cache[task_type][str(cost)]['flag']

    if filename:
        return show_lading_file(notice)
    else:
        return show_faceless(notice)


def show_landing_file(notice):
    return ''.join([fhead('TASKS'), submit_bar, fnotice(notice),
    task_description.format(filename,
                        taskname,
                        description,
                        cfg['host_ip'],
                        cfg['tasks_port'],
                        os.path.join(task_type, str(cost)))]
                    )

def show_faceless(notice):
    return ''.join([fhead('TASKS'), submit_bar, fnotice(notice),
        faceless_task.format(taskname, description)])

@app.route('/tasks')
def tasks():
    if not cfg['tasks_enabled']:
        return 'ARGHHHHHH..... Tasks are closed.'

    document = fhead('TASKS') + fhints()

    connection = sql.connect('score.db')
    q = 'select * from score;'
    res = [r for r in connection.execute(q)]

    for ttype in cache.keys():
        document += (task_row_h.format(ttype))
        for subttype in cache[ttype]:
            btn_style = 'btn-primary'
            for each in res:
                if (session.has_key('team_name') and session['team_name'] == each[0]
                    and ttype == each[1] and subttype == str(each[2])):
                    btn_style = 'btn-success'

                elif ttype == each[1] and subttype == str(each[2]):
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

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    if session.has_key('admin_token') and session['admin_token'] == secret_cfg['admin_token']:
        return _panel()
    else:
        return _log_in()

def _log_in(methods=['GET', 'POST']):
    if request.method == 'GET':
        return login_page()
    elif request.method == 'POST' and request.form['token'] == secret_cfg['admin_token']:
        session['admin_token'] = secret_cfg['admin_token']
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('index'))

@app.route('/admin/logout')
def _log_out():
    session['admin_token'] = ''
    return redirect(url_for('index'))

def login_page():
    return head + snip_login_page + footer

def _panel():
    return head + admin_menu + footer

@app.route('/admin/commits')
def _commit_table():
    document = head + admin_commit_table_head

    with open('logs/msuctf-submit.log') as f:
        o = f.readlines()

    for each in o:
        if each:
            each = each.split()
            document += admin_commit_table_cell.format(each[0], each[1], each[2], each[3], each[4], each[5], each[6])
    return document + admin_commit_table_footer

@app.route('/admin/reload/hints')
def admin_hints_reload():
    hints = loader.reload_hints()
    return redirect(url_for('admin'))

@app.route('/')
@app.route('/index')
def index():
    return fhead('HOME') + home + footer

if __name__ == '__main__':
    handler = RotatingFileHandler(cfg['errorlog'], maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.secret_key = secret_cfg['secret_key']
    app.run(host=cfg['host'], port=cfg['port'])

