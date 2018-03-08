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
    if not isinstance(error, ApiError):
        error = ApiError()

    return make_response(jsonify({
        'message': error.message or 'Unknown error',
        'code': error.error_code,
    }), error.code or 500)


class ApiError(Exception):
    message = 'Internal Error'
    code = 500

    @property
    def error_code(self):
        return self._error_code or self.code

    @error_code.setter
    def error_code(self, val):
        self._error_code = val

    def __init__(self, message=None, error_code=None, code=None):
        """
        :param message: Message to send
        :param error_code: Error specific code
        :param code: HTTP code
        """
        if message:
            self.message = message
        if error_code:
            self._error_code = error_code
        if code:
            self.code = code

    def __str__(self):
        return self.message


class InvalidUserPass(ApiError):
    code = 422
    message = 'Invalid username or password'
    _error_code = 1422


class NotAuthenticated(ApiError):
    code = 401
    message = 'Not authenticated'
    _error_code = 1401


class NoDataException(ApiError):
    code = 404
    message = 'No data found'
