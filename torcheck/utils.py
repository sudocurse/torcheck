import json
import os
from contextlib import contextmanager

NODE_LIST = "tor_nodes.txt"
DELETION_FILE = "tor_deletions.txt"

@contextmanager
def app_context(app):
    with app.app_context():
        yield

def open_delete_file(path):
    return open(os.path.join(path, DELETION_FILE), "r")

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
