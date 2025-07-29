import json
import os
import time
from tempfile import gettempdir

from requests import get

UPDATE_CREATORS_AFTER = 86400  # 1 day
IMAGE_EXTS = {"jpg", "jpeg", "png", "webp"}


# Open the JSON file
def load_json_file(path: str):
    with open(path, "r") as file:
        return json.load(file)


def save_json_file(path: str, data):
    directory = os.path.dirname(path)
    # Create all subdirectories if they do not exist
    if directory:
        os.makedirs(directory, exist_ok=True)
    # Saving the data to a file
    with open(path, "w") as file:
        json.dump(data, file)


def get_creation_time_unix(path: str):
    try:
        creation_time = os.path.getctime(path)
        return creation_time
    except Exception as e:
        return f"Error: {e}"


def download_creators(domain: str):
    url = f"https://{domain}/api/v1/creators.txt"
    print(f"Downloading: {url=}")
    r = get(url)
    r.raise_for_status()
    return r.json()


# Loads all creators
def load_creators(domain: str):
    path = os.path.join(gettempdir(), domain, "creators.txt")
    print(f"load_creators: {path=}")
    time_to_update = True
    if os.path.exists(path):
        creation_time = get_creation_time_unix(path)
        time_to_update = time.time() > creation_time + UPDATE_CREATORS_AFTER

    # download new if time_to_update
    if time_to_update:
        print(f"time_to_update: {path=}")
        data = download_creators(domain)
        save_json_file(path, data)
        return data
    else:
        return load_json_file(path)

