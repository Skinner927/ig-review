import configparser
import datetime
from flask import Blueprint, request, current_app
from passlib.hash import pbkdf2_sha256 as hashfn
import random
from . import InvalidUserPass


read_only_config = None

bp = Blueprint('authentication', __name__)


@bp.route('/current-user')
def current_user():
    return 'bob'


@bp.route('/login', methods=['POST'])
def index():
    params = request.get_json() if request.is_json else request.form

    username = params['username']
    password = params['password']

    try:
        config = configparser.RawConfigParser(current_app.config['USER_STORAGE_FILE'])
        password_hash = config.get(username, 'password')

        if not hashfn.verify(password, password_hash):
            raise InvalidUserPass()
    except configparser.Error:
        raise InvalidUserPass()

    # If we got to here, the user's password matches.
    # Let's add this to the session and

    return username
