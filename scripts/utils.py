import shutil
import requests
import json
import yaml
from datetime import datetime, timedelta

def http_get(url, params={}, headers={}, stream=False):
    """returns the jsonize responce that is fetched from the url
    if failed, it returns None
    """
    resp = requests.get(url, params=params,
                        headers=headers, stream=stream)
    resp.raise_for_status()
    return resp.json()


def http_post(url, payload={}, headers={}):
    resp = requests.post(url, data=json.dumps(payload),
                         headers=headers)
    resp.raise_for_status()
    return resp.json()

    
def download(url, path):
    resp = http_get(url, jsonify=False, stream=True)
    resp.raise_for_status()

    with open(path, "wb") as f:
        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, f)    

    
def daterange(start, end=None, time_format="%Y-%m-%d"):
    if type(start) is str:
        start = datetime.strptime(start, time_format).date()
    if type(end) is str:
        end = datetime.strptime(end, time_format).date()
    elif end is None:
        end = datetime.now().date()
        
    for n in range((end - start).days):
        yield start + timedelta(n)

        
def get_timestamp(time_format="%Y-%m-%d", return_str=True):
    now = datetime.now()
    if return_str:
        return now.strftime(time_format)
    else:
        return now


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)
    
