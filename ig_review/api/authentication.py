import configparser
import datetime
from flask import Blueprint, request, current_app, session, make_response, jsonify
from passlib.hash import pbkdf2_sha256 as hashfn
import random
from . import InvalidUserPass, NotAuthenticated


read_only_config = None
_SESSION_KEYS = ['username', 'unique']

bp = Blueprint('authentication', __name__)


@bp.route('/user/status')
def current_user():
    return validate_current_user()


@bp.route('/user/login', methods=['POST'])
def index():
    params = request.get_json() if request.is_json else request.form

    username = params['username']
    password = params['password']

    wipe_session()
    config = get_fresh_config()
    if not config.has_section(username):
        raise InvalidUserPass()

    password_hash = config.get(username, 'password', fallback=None)

    if password_hash is None:
        # No password hash, so this login is actually to setup the initial password
        config.set(username, 'password', hashfn.hash(password))
    elif not hashfn.verify(password, password_hash):
        raise InvalidUserPass()

    # If we got to here, the user's password matches (or its new).
    # Let's add this to the session and update 'unique'
    unique = '%032x' % random.getrandbits(128)
    session['unique'] = unique
    session['username'] = username
    config.set(username, 'unique', unique)

    with open(current_app.config['USER_STORAGE_FILE'], 'w') as f:
        config.write(f)

    global read_only_config
    read_only_config = config

    return make_response(jsonify({
        'username': username,
    }))


@bp.route('/user/logout')
def logout():
    wipe_session()
    return make_response(jsonify({'message': 'success'}))


def wipe_session():
    for key in _SESSION_KEYS:
        session[key] = None


def get_fresh_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read(current_app.config['USER_STORAGE_FILE'])
    return config


def validate_current_user():
    username = session.get('username', None)
    unique = session.get('unique', None)

    if not username or not unique:
        raise NotAuthenticated()

    config = read_only_config or get_fresh_config()

    try:
        if config.get(username, 'unique') != unique:
            wipe_session()
            raise NotAuthenticated()
    except configparser.Error:
        wipe_session()
        raise NotAuthenticated()

    return make_response(jsonify({
        'username': username
    }))
