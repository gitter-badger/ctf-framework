from flask import Blueprint


view_blueprint = Blueprint(
    'view', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/view'
)

import view.views
