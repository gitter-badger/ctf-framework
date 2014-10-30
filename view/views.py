import os

from flask import redirect, render_template, request, url_for, session
from flask import send_from_directory
from flask import current_app as app
from sqlalchemy.orm import sessionmaker

from view import view_blueprint as view
from controller import get_tasks, get_task_info
from controller import get_scoreboard, get_solved_tasks, get_teamdata
from controller import get_hints, get_commits, get_tasknametype_by_id
from controller import is_flag_valid, proceed_teamdata

@view.route('/')
@view.route('/index')
def index_page():
    return render_template('index.html')

@view.route('/tasks')
def tasks_page():
    if app.config['admin_access_only'] \
            and session.get('token', '') != app.config.get('admin_token'):
        return render_template('locked.html')
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
def task_unit_page(tid):
    if app.config['admin_access_only'] \
            and session.get('token', '') != app.config.get('admin_token'):
        return render_template('locked.html')
    if not app.config['tasks_opened']:
        return render_template('locked.html')
    task_info = get_task_info(tid)
    hints = get_hints(tid)
    if task_info and task_info.enabled:
        return render_template('task_unit.html',
                                task_info=task_info,
                                teamholder=session.get('teamname', ''),
                                hints=hints)
    return render_template('locked.html')

@view.route('/scoreboard')
def scoreboard_page():

    if app.config['admin_access_only'] \
            and session.get('token', '') != app.config.get('admin_token'):
        return render_template('locked.html')
    if not app.config['scoreboard_opened']:
        return render_template('locked.html')
    scoreboard_info = get_scoreboard()
    return render_template('scoreboard.html', info=scoreboard_info)

@view.route('/scoreboard/<string:teamname>')
def team_profile(teamname):
    teamdata = get_teamdata(teamname)
    taskdata = [(get_tasknametype_by_id(flag.task_id), \
                flag.datetime.replace(microsecond=0)) \
                for flag in teamdata if flag.result == 'success']
    commits = {}
    for commit in taskdata:
        tasktype = commit[0][1]
        if not tasktype in commits.keys():
            commits[tasktype] = 0
        commits[tasktype] += 1

    if not app.config['scoreboard_opened'] or not teamdata:
        return render_template('locked.html')
    pts, solved, last_commit = proceed_teamdata(teamdata)
    return render_template('teamprofile.html',
                            teamname=teamname,
                            taskdata=taskdata,
                            commits=commits.items(),
                            pts=pts,
                            solved=solved,
                            last_commit=last_commit.replace(microsecond=0))

@view.route('/write-ups')
def write_ups_page():
    if not app.config['writeups_opened']:
        return render_template('locked.html')
    return render_template('write-ups.html', config=app.config)

@view.route('/commit', methods=['POST'])
def commit_flag():
    if not app.config['tasks_opened']:
        return redirect('/index')
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
def admin_panel():
    if not session['token'] == app.config.get('admin_token'):
        return render_template('locked.html')
    return render_template('admin_panel.html')

@view.route('/admin/logout')
def admin_logout():
    session['token'] = ''
    return redirect('/index')

@view.route('/admin/configure')
def configure(methods=['POST']):
    if not session['token'] == app.config.get('admin_token'):
        return render_template('locked.html')
    # TODO: configure here
    return redirect('/admin_panel')

@view.route('/admin/commits')
def show_commits():
    if not session['token'] == app.config.get('admin_token'):
        return render_template('locked.html')
    commits = get_commits()
    return render_template('commits.html', commits=commits)

@view.route('/files/<path:task>/<path:filename>')
def return_static_file(task, filename):
    if not app.config['tasks_opened']:
        return redirect('/index')
    return send_from_directory(os.path.join('files/tasks/', task),
                               filename,
                               as_attachment=True)

