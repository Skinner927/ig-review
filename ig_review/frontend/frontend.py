from flask import Blueprint, send_from_directory, current_app, session

bp = Blueprint('frontend', __name__)


@bp.route('/images/<path:p>')
def index(p):
    return send_from_directory(current_app.config['IMAGES_REVIEW_DIR'], p)


@bp.route('/', defaults={'p': 'index.html'})
@bp.route('/<path:p>')
def content(p):
    return send_from_directory('static', p)
