from flask import jsonify, make_response
from .. import factory


def create_app(settings_override=None):
    app = factory.create_app(__name__, __path__, settings_override)

    # Simple debug route
    app.add_url_rule('/ping', 'ping', lambda: 'pong')

    # Catch all API errors and convert them to json
    app.register_error_handler(Exception, error_handler)

    return app


def error_handler(error):
    return make_response(jsonify({
        'message': error.message if hasattr(error, 'message') else 'Unknown error',
    }), error.code if hasattr(error, 'code') else 500)


class ApiError(Exception):
    message = 'Internal Error'
    code = 500

    def __init__(self, message=None, code=None):
        if message:
            self.message = message
        if code:
            self.code = code

    def __str__(self):
        return self.message


class InvalidUserPass(ApiError):
    code = 400
    message = 'Invalid username or password'