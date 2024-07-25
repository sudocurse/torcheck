import json
from contextlib import contextmanager


@contextmanager
def app_context(app):
    with app.app_context():
        yield

def define_response(app, data):
    return app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )

def define_error(app, message, status=400):
    return app.response_class(
        response=json.dumps({"status": "error", "message": message}),
        status=status,
        mimetype='application/json'
    )
