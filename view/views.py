import os
from functools import wraps

from flask import redirect, render_template, request, url_for, session
from flask import send_from_directory
from flask import current_app as app
from sqlalchemy.orm import sessionmaker

from view import view_blueprint as view
from controller import get_tasks, get_task_info, get_less_results
from controller import get_scoreboard, get_solved_tasks, get_teamdata
from controller import get_hints, get_commits, get_tasknametype_by_id
from controller import is_flag_valid, proceed_teamdata, get_result_list
from controller import create_session, get_global_stats, edit_settings
from controller.database import establish_connection


def admin_only(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwds):
        if app.config['admin_access_only'] \
                and session.get('token', '') != app.config.get('admin_token'):
            return render_template('locked.html')
        return view_func(*args, **kwds)
    return wrapper

def scoreboard_opened(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwds):
        if not app.config['scoreboard_opened']:
            return render_template('locked.html')
        return view_func(*args, **kwds)
    return wrapper

def tasks_opened(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwds):
        if not app.config['tasks_opened']:
            return render_template('locked.html')
        return view_func(*args, **kwds)
    return wrapper

def admin_access(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwds):
        if not session['token'] == app.config.get('admin_token'):
            return render_template('locked.html')
        return view_func(*args, **kwds)
    return wrapper

@view.route('/')
@view.route('/index')
def index_page():
    return render_template('index.html')

@view.route('/tasks')
@admin_only
@tasks_opened
def tasks_page():
    tasks = get_tasks()
    items = {}
    for task in tasks:
        if items.get(task.tasktype, ''):
            items[task.tasktype].append(task)
        else:
            items[task.tasktype] = [task]
    solved_tasks = get_solved_tasks(session.get('teamname', ''))
    solved_tasks = [solv[0] for solv in solved_tasks]
    return render_template('tasks.html', tasks=items,
                           config=app.config, solved_tasks=solved_tasks)

@view.route('/task/<int:tid>')
@tasks_opened
@admin_only
def task_unit_page(tid):
    task_info = get_task_info(tid)
    hints = get_hints(tid)
    if task_info and task_info.enabled:
        return render_template('task_unit.html',
                                task_info=task_info,
                                teamholder=session.get('teamname', ''),
                                hints=hints)
    return render_template('locked.html')

@view.route('/scoreboard')
@admin_only
@scoreboard_opened
def scoreboard_page():
    scoreboard_info = get_scoreboard()
    return render_template('scoreboard.html', info=scoreboard_info)

@view.route('/global_stats')
@admin_only
def global_stats():
    return render_template('global_stats.html')

@view.route('/scoreboard/<string:teamname>')
@scoreboard_opened
@admin_only
def team_profile(teamname):
    teamdata = get_teamdata(teamname)
    if not teamdata:
        return render_template('locked.html')
    taskdata = [(get_tasknametype_by_id(flag.task_id), \
                flag.datetime.replace(microsecond=0)) \
                for flag in teamdata if flag.result == 'success']
    commits = {}
    for commit in taskdata:
        tasktype = commit[0][1]
        if not tasktype in commits.keys():
            commits[tasktype] = 0
        commits[tasktype] += 1

    pts, solved, last_commit = proceed_teamdata(teamdata)
    return render_template('teamprofile.html',
                            teamname=teamname,
                            taskdata=taskdata,
                            commits=commits.items(),
                            pts=pts,
                            solved=solved,
                            last_commit=last_commit.replace(microsecond=0))

@view.route('/netcat')
def netcat():
    return render_template('netcat.html')

@view.route('/results')
@admin_only
def result_list():
    if not app.config['results_opened']:
        return render_template('locked.html')
    results = get_result_list()
    return render_template('result_list.html',
                            config=app.config,
                            competitions=results.keys())

@view.route('/results/<int:rid>')
@admin_only
def result_less_page(rid):
    if not app.config['results_opened']:
        return render_template('locked.html')

    databases = get_result_list()
    if rid - 1 > len(databases.values()):
        return render_template('locked.html')
    session = create_session(establish_connection(app.config['scheme'] \
                                                + databases.values()[rid - 1]))
    info = get_less_results(session)
    total_tasks, total_tasks_solved, total_commits, total_valid_commits, \
        total_teams, stats  = get_global_stats(session)
    return render_template('results_less.html', info=info,
                            rid=rid, comp_name=databases.keys()[rid - 1],
                            total_tasks=total_tasks,
                            total_tasks_solved=total_tasks_solved,
                            total_commits=total_commits,
                            total_valid_commits=total_valid_commits,
                            total_teams=total_teams, stats=stats)

@view.route('/results/<int:rid>/<string:teamname>')
@admin_only
def result_more_page(rid, teamname):
    if not app.config['results_opened']:
        return render_template('locked.html')
    databases = get_result_list()
    databases = get_result_list()
    if rid - 1 > len(databases.values()):
        return render_template('locked.html')

    session = create_session(establish_connection(
        app.config['scheme'] + databases.values()[rid - 1])
    )
    teamdata = get_teamdata(teamname, session)
    if not teamdata:
        return render_template('locked.html')

    taskdata = [(get_tasknametype_by_id(flag.task_id, session), \
                flag.datetime.replace(microsecond=0)) \
                for flag in teamdata if flag.result == 'success']
    commits = {}

    for commit in taskdata:
        tasktype = commit[0][1]
        if not tasktype in commits.keys():
            commits[tasktype] = 0
        commits[tasktype] += 1

    pts, solved, last_commit = proceed_teamdata(teamdata)
    return render_template('teamprofile.html',
                            teamname=teamname,
                            taskdata=taskdata,
                            commits=commits.items(),
                            pts=pts,
                            solved=solved,
                            last_commit=last_commit.replace(microsecond=0))

@view.route('/commit', methods=['POST'])
@tasks_opened
@admin_only
def commit_flag():
    if request.form.has_key('teamname'):
        session['teamname'] = request.form.get('teamname')
    rcode = is_flag_valid(request.form, request.remote_addr)
    if rcode == 101:
        return render_template('success.html', args=request.form)
    elif rcode == 202:
        return render_template('fail.html')
    elif rcode == 303:
        return render_template('already_submitted.html')

@view.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if session.get('token', '') == app.config.get('admin_token'):
        return redirect('/admin_panel')
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.form.has_key('token') and \
            request.form.get('token') == app.config.get('admin_token'):
        session['token'] = app.config.get('admin_token')
        return redirect('/admin_panel')
    return render_template('locked.html')

@view.route('/admin_panel')
@admin_access
def admin_panel():
    return render_template('admin_panel.html')

@view.route('/admin/logout')
def admin_logout():
    session['token'] = ''
    return redirect('/index')

@view.route('/admin/configure', methods=['POST'])
def configure():
    if not session['token'] == app.config.get('admin_token'):
        return render_template('locked.html')
    edit_settings(request.form)
    return redirect('/admin_panel')

@view.route('/admin/commits')
@admin_access
def show_commits():
    commits = get_commits()
    return render_template('commits.html', commits=commits)

@view.route('/files/<path:task>/<path:filename>')
@tasks_opened
@admin_only
def return_static_file(task, filename):
    return send_from_directory(os.path.join('files/tasks/', task),
                               filename,
                               as_attachment=True)

