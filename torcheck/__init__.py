from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py")

    @app.route('/source')
    def source():
        return app.config["SERVICES"]["tor"]["node_list"]

    return app