from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import contextmanager
from flask import current_app as app
import os
import requests


CACHE_FILE = "tor_nodes.txt"

@contextmanager
def app_context():
    with app.app_context():
        yield

def schedule_download(source_url, path, cfg):
    try:
        response = requests.get(source_url)
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
        source_url = cfg["source_url"]

        path = os.path.join(app.instance_path, CACHE_FILE)
        interval = cfg["refresh_interval"]

        schedule_download(source_url, path, app.config) # initial

        scheduler = BackgroundScheduler()
        scheduler.add_job(schedule_download, "interval", seconds=interval,
                          args=[source_url, path, cfg])
        scheduler.start()
