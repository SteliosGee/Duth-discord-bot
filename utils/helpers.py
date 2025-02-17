import requests
import os
import json

def check_server_status(url):
    try:
        response = requests.get(url, timeout=10)
        return (True, "Server is up and running") if response.status_code == 200 else (False, "Server is down")
    except requests.RequestException:
        return False, "Server is not reachable"

def load_last_guid():
    print(os.getcwd())
    with open("data/last_guid.txt") as f:
        return f.read().strip()
    return None

def save_last_guid(guid):
    with open("data/last_guid.txt", "w") as f:
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