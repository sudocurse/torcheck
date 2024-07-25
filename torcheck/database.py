from ipaddress import ip_address
from torcheck.utils import app_context, open_delete_file

def match_ip(user_input, addresses):
    try:
        user_ip = ip_address(user_input.strip("[]").strip())
    except ValueError:
        return False
    return user_ip in addresses

def update_cache(app, nodes):
    # parse response.content to list and set config["SERVICES"]["tor"]["nodes"]
    with app_context(app):
        try:
            # TODO: only ~6500 lines, if it was significantly more, i'd think about the data structure
            app.config["SERVICES"]["tor"]["nodes"] = [ip_address(n.strip().strip("[]"))
                                                      for n in nodes if n and not was_deleted(n, app)]
        except ValueError:
            source = app.config["SERVICES"]["tor"]["source_url"]
            raise Exception(f"Invalid IP address in source list {source}")

def was_deleted(ip, app):
    with app_context(app):
        with open_delete_file(app.instance_path) as f:
            deletions = f.readlines()
        return ip in deletions

def save_deletion(ip, app):
    # TODO: thread with a queue for writes
    with app_context(app):
        with open_delete_file(app.instance_path) as f:
            f.write(f"{ip}\n")

def delete_node(ip, app):
    with app_context(app):
        if ip in app.config["SERVICES"]["tor"]["nodes"]:
            app.config["SERVICES"]["tor"]["nodes"].remove(ip)
            save_deletion(ip)
            return True
    return False
