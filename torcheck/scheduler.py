from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import contextmanager
from flask import current_app as app
import os
import requests


@contextmanager
def app_context():
    with app.app_context():
        yield

def schedule_download(node_list, path):
    try:
        response = requests.get(node_list)
        with open(path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        raise Exception("Error downloading node list")

def start_scheduler(app):
    with app.app_context():
        node_list = app.config["SERVICES"]["tor"]["node_list"]
        path = os.path.join(app.instance_path, "tor_nodes.txt")

    schedule_download(node_list, path)
    scheduler = BackgroundScheduler()
    scheduler.add_job(schedule_download, "interval", seconds=60 * 60, args=[node_list, path])
    scheduler.start()
