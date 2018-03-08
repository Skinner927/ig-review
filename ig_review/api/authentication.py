import configparser
from flask import Blueprint, request, current_app, session, make_response, jsonify
from functools import wraps
from passlib.hash import pbkdf2_sha256 as hashfn
import random
from . import InvalidUserPass, NotAuthenticated


_config = configparser.ConfigParser(interpolation=None)
_SESSION_KEYS = ['username', 'unique']

bp = Blueprint('authentication', __name__)


@bp.route('/user/current')
def current_user():
    return make_response(jsonify(validate_current_user()))


@bp.route('/user/login', methods=['POST'])
def index():
    global _config
    params = request.get_json() if request.is_json else request.form

    username = params['username']
    password = params['password']

    wipe_session()
    refresh_config()
    if not _config.has_section(username):
        raise InvalidUserPass()

    password_hash = _config.get(username, 'password', fallback=None)

    if password_hash is None:
        # No password hash, so this login is actually to setup the initial password
        _config.set(username, 'password', hashfn.hash(password))
    elif not hashfn.verify(password, password_hash):
        raise InvalidUserPass()

    # If we got to here, the user's password matches (or its new).
    # Let's add this to the session and update 'unique'
    unique = '%032x' % random.getrandbits(128)
    session['unique'] = unique
    session['username'] = username
    _config.set(username, 'unique', unique)

    with open(current_app.config['USER_STORAGE_FILE'], 'w') as f:
        _config.write(f)

    return make_response(jsonify({
        'username': username,
    }))


@bp.route('/user/logout', methods=['GET', 'POST'])
def logout():
    wipe_session()
    return make_response(jsonify({'message': 'success'}))


def wipe_session():
    for key in _SESSION_KEYS:
        session[key] = None


def refresh_config():
    global _config
    _config.read(current_app.config['USER_STORAGE_FILE'])


def validate_current_user():
    global _config
    username = session.get('username', None)
    unique = session.get('unique', None)

    if not username or not unique:
        # For sure not authenticated as session is empty
        raise NotAuthenticated()

    try:
        if not _config.has_section(username):
            refresh_config()

        if _config.get(username, 'unique') != unique:
            wipe_session()
            raise NotAuthenticated()
    except configparser.Error:
        wipe_session()
        raise NotAuthenticated()

    return {'username': username}


def require_login(func):
    """
    Decorator for routes that require authentication
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        validate_current_user()
        return func(*args, **kwargs)
    return wrapper
