from flask import Flask, request
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

    def define_error(message, status=400):
        return app.response_class(
            response=json.dumps({"status": "error", "message": message}),
            status=status,
            mimetype='application/json'
        )

    @app.route('/source')
    def source():
        data = {"source": cfg["source_url"]}
        return define_response(data)

    @app.route('/nodes')
    def nodes():
        data = {"nodes": cfg["nodes"]}
        return define_response(data)

    @app.route('/node/<ip>', methods=['GET', 'DELETE'])
    def node(ip=None):
        if not ip:
            return define_error("IP not provided", 400)

        if request.method == 'GET':
            return define_response({"tor": ip in cfg["nodes"]})

        if request.method == 'DELETE':
            if ip in cfg["nodes"]:
                cfg["nodes"].remove(ip)
                scheduler.delete_from_cache(ip)
                return define_response({"status": "success"})

            else:
                return define_error("Node not found", 404)

    scheduler.start_scheduler(app)

    return app
