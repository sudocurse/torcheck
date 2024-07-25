from ipaddress import ip_address
import os

from torcheck.utils import app_context

CACHE_FILE = "tor_nodes.txt"

def match_ip(user_input, addresses):
    try:
        user_ip = ip_address(user_input.strip("[]").strip())
    except ValueError:
        return False
    return user_ip in addresses

def delete_node(ip, app):
    with app_context(app):
        nodes = app.config["SERVICES"]["tor"]["nodes"]
        if ip in nodes:
            nodes.remove(ip)
            app.config["SERVICES"]["tor"]["nodes"] = nodes
            delete_from_cache(ip)
            return True
        else:
            return False
    return False

def delete_from_cache(ip, app):
    # TODO: thread with a queue for writes
    with app_context(app):
        path = os.path.join(app.instance_path, CACHE_FILE)
        with open(path, "r") as f:
            nodes = f.readlines()

        with open(path, "w") as f:
            for node in nodes:
                if node.strip() != ip:
                    f.write(node)

def update_cache(app, nodes):
    # parse response.content to list and set config["SERVICES"]["tor"]["nodes"]
    with app_context(app):
        try:
            # TODO: only ~6500 lines, if it was significantly more, i'd think about the data structure
            app.config["SERVICES"]["tor"]["nodes"] = [ip_address(n.strip().strip("[]"))
                                                      for n in nodes if n]
        except ValueError:
            source = app.config["SERVICES"]["tor"]["source_url"]
            raise Exception(f"Invalid IP address in source list {source}")
