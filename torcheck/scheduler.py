from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import contextmanager
from flask import current_app as app
import os
import requests


@contextmanager
def app_context():
    with app.app_context():
        yield

def schedule_download(node_list, path, cfg):
    try:
        response = requests.get(node_list)
        with open(path, "wb") as f:
            f.write(response.content)

        # parse response.content to list and set config["SERVICES"]["tor"]["nodes"]
        with app_context():
            nodes = response.content.decode("utf-8").split("\r\n")
            app.config["SERVICES"]["tor"]["nodes"] = [n.strip() for n in nodes]

    except Exception as e:
        raise Exception("Error downloading node list")

def start_scheduler(app):

    with app.app_context():
        cfg = app.config["SERVICES"]["tor"]
        node_list = cfg["node_list"]
        path = os.path.join(app.instance_path, "tor_nodes.txt")
        interval = cfg["refresh_interval"]

        schedule_download(node_list, path, app.config) # initial

        scheduler = BackgroundScheduler()
        scheduler.add_job(schedule_download, "interval", seconds=interval,
                          args=[node_list, path, cfg])
        scheduler.start()
