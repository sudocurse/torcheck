from flask import Flask
from . import scheduler
import json



def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")
    cfg = app.config["SERVICES"]["tor"]

    def define_response(data):
        return app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )

    @app.route('/source')
    def source():
        data = {"source": cfg["node_list"]}
        return define_response(data)

    @app.route('/list')
    def list():
        data = {"nodes": cfg["nodes"]}
        return define_response(data)

    scheduler.start_scheduler(app)

    return app