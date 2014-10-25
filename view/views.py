from flask import redirect, render_template, request, url_for, session
from flask import current_app as app

from view import view_blueprint as view
from sqlalchemy.orm import sessionmaker
from controller import get_tasks, get_task_info
from controller import get_scoreboard, get_solved_tasks
from controller import get_hints, get_commits
from controller import is_flag_valid

@view.route('/')
@view.route('/index')
def index_page():
    return render_template('index.html')

@view.route('/tasks')
def tasks_page():
    tasks = get_tasks()
    items = {}
    for task in tasks:
        if items.get(task.tasktype, ''):
            items[task.tasktype].append(task)
        else:
            items[task.tasktype] = [task]
    solved_tasks = get_solved_tasks(session['teamname'])
    solved_tasks = [solv[0] for solv in solved_tasks]
    return render_template('tasks.html', tasks=items,
                           config=app.config, solved_tasks=solved_tasks)

@view.route('/task/<int:tid>')
def task_unit_page(tid):
    if not app.config['tasks_opened']:
        return render_template('locked.html')
    task_info = get_task_info(tid)
    hints = get_hints(tid)
    if task_info and task_info.enabled:
        return render_template('task_unit.html',
                               task_info=task_info, hints=hints)
    return render_template('locked.html')

@view.route('/scoreboard')
def scoreboard_page():
    if not app.config['scoreboard_opened']:
        return render_template('locked.html')
    scoreboard_info = get_scoreboard()
    return render_template('scoreboard.html', info=scoreboard_info)

@view.route('/write-ups')
def write_ups_page():
    if not app.config['writeups_opened']:
        return render_template('locked.html')
    return render_template('write-ups.html', config=app.config)

@view.route('/commit', methods=['POST'])
def commit_flag():
    if app.config['tasks_opened']:
        if request.form.has_key('teamname'):
            session['teamname'] = request.form.get('teamname')
        rcode = is_flag_valid(request.form, request.remote_addr)
        if rcode == 101:
            return render_template('success.html', args=request.form)
        elif rcode == 202:
            return render_template('fail.html')
        elif rcode == 303:
            return render_template('already_submitted.html')
    return ''

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
    if not session['token'] == app.config.get('admin_token'):
        return render_template('locked.html')
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

