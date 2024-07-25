from flask import Flask, request

import torcheck.scheduler as scheduler
import torcheck.database as db
from .utils import define_response, define_error


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")
    cfg = app.config["SERVICES"]["tor"]

    scheduler.start_scheduler(app)

    @app.route('/source')
    def source():
        data = {"source": cfg["source_url"]}
        return define_response(app, data)

    @app.route('/nodes')
    def nodes():
        data = {"nodes": [str(ip) for ip in cfg["nodes"]]}
        return define_response(app, data)

    @app.route('/node/<ip>', methods=['GET', 'DELETE'])
    def node(ip=None):
        if not ip:
            return define_error(app, "IP not provided", 400)

        if request.method == 'GET':
            try:
                return define_response(app, {
                    "tor": db.match_ip(ip, cfg["nodes"])
                })
            except Exception as e:
                return define_error(app, "Error matching IP", 500)

        if request.method == 'DELETE':
            if db.delete_node(ip, cfg["nodes"]):
                return define_response(app, {"status": "success"})
            else:
                return define_error(app, "Node not found", 404)

    @app.route('/delete/<ip>', methods=['GET']) # convenience route for this assignment
    def delete(ip=None):
        if not ip:
            return define_error(app, "IP not provided", 400)

        if db.delete_node(ip, app):
            return define_response(app, {"status": "success"})
        else:
            return define_error(app, "Node not found", 404)

    def test_match_ipv6(): #TODO: put this in a proper test file
        # test with a valid but weirdly formatted ipv6 address
        test_ipv6 = "2a0b:F4C2:1:0000:00:0::138   "
        assert db.match_ip(test_ipv6, cfg["nodes"])

    return app
