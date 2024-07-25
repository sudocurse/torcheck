from ipaddress import ip_address
from torcheck.utils import app_context, get_delete_file

def match_ip(user_input, addresses):
    try:
        user_ip = ip_address(user_input.strip("[]").strip())
    except ValueError:
        return False
    return user_ip in addresses

def update_cache(app, nodes):
    # parse response.content to list and set config["SERVICES"]["tor"]["nodes"]
    with app_context(app):
        # TODO: only ~6500 lines, if it was significantly more, i'd think about the data structure
        nodes = [ip_address(n.strip().strip("[]")) for n in nodes if not was_deleted(n, app)]
        app.config["SERVICES"]["tor"]["nodes"] = nodes

def was_deleted(ip, app):
    with app_context(app):
        with open(get_delete_file(app.instance_path), 'r') as f:
            deletions = f.readlines()
        return ip in deletions

def save_deletion(ip, app):
    # TODO: thread with a queue for writes
    with app_context(app):
        with open(get_delete_file(app.instance_path), 'w') as f:
            f.write(f"{ip}\n")

def delete_node(ip, app):
    with app_context(app):
        if match_ip(ip, app.config["SERVICES"]["tor"]["nodes"]):
            app.config["SERVICES"]["tor"]["nodes"].remove(ip_address(ip))
            save_deletion(ip, app)
            return True
    return False
