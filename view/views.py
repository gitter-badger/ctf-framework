from flask import redirect, render_template, request, url_for

from view import view_blueprint as view


@view.route('/')
@view.route('/index')
def index_page():
    return render_template('index.html')

@view.route('/tasks')
def task_page():
    return render_template('tasks.html')

@view.route('/scoreboard')
def scoreboard_page():
    return render_template('scoreboard.html')

@view.route('/write-ups')
def write_ups_page():
    return render_template('write-ups.html')

