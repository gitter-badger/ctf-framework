from flask import redirect, render_template, request, url_for
from flask import current_app as app

from view import view_blueprint as view
from sqlalchemy.orm import sessionmaker
from controller import get_tasks, get_task_info

@view.route('/')
@view.route('/index')
def index_page():
    return render_template('index.html')

@view.route('/tasks')
def tasks_page():
    tasks = get_tasks(app.config)
    items = {}
    for task in tasks:
        if items.get(task.tasktype, ''):
            items[task.tasktype].append(task)
        else:
            items[task.tasktype] = [task]
    return render_template('tasks.html', tasks=items, config=app.config)

@view.route('/task/<int:id>')
def task_unit_page(id):
    if not app.config['tasks_opened']:
        return render_template('locked.html')
    task_info = get_task_info(app.config, id)
    hints = {}
    if task_info: #and task_info.enabled:
        return render_template('task_unit.html',
                               task_info=task_info, hints=hints)
    return render_template('locked.html')


@view.route('/scoreboard')
def scoreboard_page():
    if not app.config['scoreboard_opened']:
        return render_template('locked.html')
    return render_template('scoreboard.html', config=app.config)

@view.route('/write-ups')
def write_ups_page():
    return render_template('write-ups.html', config=app.config)

