#!/usr/bin/python3

import time
import json
from pprint import pprint
import unittest
from random import randint
from datetime import datetime

import requests

class ZenobaseAPI():
    def __init__(self, username, password):
        r = requests.post("https://api.zenobase.com/oauth/token", data={"grant_type": "password", "username": username, "password": password})
        data = r.json()
        if "error" in data:
            raise Exception("Invalid Zenobase credentials")
        self.access_token = data["access_token"]
        self.client_id = data["client_id"]
  
    def _request(self, method, endpoint, data=None, headers={}):
        url = "https://api.zenobase.com" + endpoint
        headers["Authorization"] = "Bearer {}".format(self.access_token)
        headers["Content-Type"] = "application/json"
        args = [url]
        kwargs = {"data": json.dumps(data), "headers": headers}
        if method == "GET":
            r = requests.get(*args, **kwargs)
        elif method == "POST":
            r = requests.post(*args, **kwargs)
        elif method == "DELETE":
            r = requests.delete(*args, **kwargs)
        else:
            raise Exception("UNSUPPORTED METHOD")

        if 300 < r.status_code:
            raise Exception("Status code was not 2xx: {}".format(r))

        if "content-type" in r.headers:
            if "application/json" in r.headers["content-type"]:
                return r.json()
        return r.text

    def get(self, *args, **kwargs):
        return self._request("GET", *args, **kwargs)
    
    def post(self, *args, **kwargs):
        return self._request("POST", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request("DELETE", *args, **kwargs)

    def list_buckets(self):
        return self.get("/users/{}/buckets/".format(self.client_id))

    def get_bucket(self, bucket_id):
        return self.get("/buckets/{}".format(bucket_id))

    def create_bucket(self, label, description=""):
        if not 1 <= len(label) <= 20:
            raise Exception("Bucket name must be 1-20 chars and can only contain [a-zA-Z0-9-_ ]")
        return self.post("/buckets/", data={"label": label, "description": description})

    def create_or_get_bucket(self, label, description=""):
        data = self.list_buckets()
        for bucket in data["buckets"]:
            if bucket["label"] == label:
                return bucket
        return self.create_bucket(label, description=description)

    def delete_bucket(self, bucket_id):
        self.delete("/buckets/{}".format(bucket_id))

    def list_events(self, bucket_id):
        return self.get("/buckets/{}/".format(bucket_id))

    def create_event(self, bucket_id, event):
        assert isinstance(event, ZenobaseEvent) or isinstance(event, dict)
        return self.post("/buckets/{}/".format(bucket_id), data=event)


_VALID_FIELDS = ["bits", "concentration", "count", "distance", 
                 "duration", "energy", "frequency", "height", 
                 "humidity", "location", "note", "moon", "percentage", 
                 "pressure", "rating", "resource", "sound", "source", "tag", 
                 "temperature", "timestamp", "velocity", "volume", "weight"]


class ZenobaseEvent(dict):
    """
        Provides simple structure checking
    """
    def __init__(self, data):
        for field in data:
            assert field in _VALID_FIELDS
            self[field] = data[field]

def dt_to_timestamp(dt, timezone="+00:00"):
    return datetime.strftime(dt, "%Y-%m-%dT%H:%M:%S") + ".000" + timezone
