import os

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from torcheck.database import update_cache, CACHE_FILE
from torcheck.utils import app_context


def schedule_download(source_url, path, app):
    try:
        response = requests.get(source_url)
        with open(path, "wb") as f:
            f.write(response.content)

        nodes = response.content.decode("utf-8").split("\r\n")
        update_cache(app, nodes)

    except Exception as e:
        raise Exception("Error downloading node list")


def start_scheduler(app):
    with app_context(app):
        cfg = app.config["SERVICES"]["tor"]
        source_url = cfg["source_url"]

        path = os.path.join(app.instance_path, CACHE_FILE)
        interval = cfg["refresh_interval"]

        # initially check if we can read file, else download
        if os.path.exists(path):
            with open(path, "r") as f:
                nodes = f.readlines()
            update_cache(app, nodes)
        else:
            schedule_download(source_url, path, app)

        scheduler = BackgroundScheduler()
        scheduler.add_job(schedule_download, "interval", seconds=interval,
                          args=[source_url, path, app])
        scheduler.start()
