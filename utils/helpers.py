import requests
import json

def check_server_status(url):
    try:
        response = requests.get(url, timeout=10)
        return (True, "Server is up and running") if response.status_code == 200 else (False, "Server is down")
    except requests.RequestException:
        return False, "Server is not reachable"

import os

# Get the absolute path of the duth_bot directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Adjust if needed

def get_data_path(filename):
    return os.path.join(BASE_DIR, "data", filename)

def load_last_guid():
    print(os.getcwd())  # Debugging: Check working directory
    file_path = get_data_path("last_guid.txt")
    with open(file_path) as f:
        return f.read().strip()
    return None

def save_last_guid(guid):
    file_path = get_data_path("last_guid.txt")
    with open(file_path, "w") as f:
        f.write(guid)


async def save_message_id(message_id):
    with open('data/status_message_id.json', 'w') as f:
        json.dump({"message_id": message_id}, f)

async def load_message_id():
    if os.path.exists('data/status_message_id.json'):
        with open('data/status_message_id.json', 'r') as f:
            data = json.load(f)
            return data.get("message_id")
    return None

print(load_last_guid()) # Debug print