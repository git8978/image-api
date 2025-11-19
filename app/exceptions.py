# app/exceptions.py

from flask import jsonify

class APIError(Exception):
    """Base class for API exceptions."""
    status_code = 500
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class NotFoundError(APIError):
    status_code = 404

class InvalidInputError(APIError):
    status_code = 400

def register_error_handlers(app):
    """Registers global error handler for custom API exceptions."""
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response