import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from torcheck.database import update_cache
from torcheck.utils import app_context, NODE_LIST


def schedule_download(source_url, path, app):
    response = requests.get(source_url)
    with open(path, "wb") as f:
        f.write(response.content)

    nodes = response.content.decode("utf-8").split("\r\n")
    update_cache(app, nodes)

def start_scheduler(app):
    with app_context(app):
        cfg = app.config["SERVICES"]["tor"]
        source_url = cfg["source_url"]

        os.makedirs(app.instance_path, exist_ok=True)

        # make sure delete file exists
        delete_file = os.path.join(app.instance_path, "tor_deletions.txt")
        if not os.path.exists(delete_file):
            with open(delete_file, "a"):
                pass

        node_list_path = os.path.join(app.instance_path, NODE_LIST)
        interval = cfg["refresh_interval"]

        # initially check if we can read file, else download
        if os.path.exists(node_list_path):
            with open(node_list_path, "r") as f:
                nodes = f.readlines()
            update_cache(app, nodes)
        else:
            schedule_download(source_url, node_list_path, app)

        scheduler = BackgroundScheduler()
        scheduler.add_job(schedule_download, "interval", seconds=interval,
                          args=[source_url, node_list_path, app])
        scheduler.start()
