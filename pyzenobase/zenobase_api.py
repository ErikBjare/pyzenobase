import json
import requests
from pyzenobase import ZenobaseEvent


class ZenobaseAPI:
    # TODO: Keep track of open/closed state internally

    HOST = "https://api.zenobase.com"

    def __init__(self, username=None, password=None):
        payload = {}
        if username is not None:
            payload = {"grant_type": "password", "username": username, "password": password}
        else:
            payload = {"grant_type": "client_credentials"}
        r = requests.post(self.HOST + "/oauth/token", data=payload)
        data = r.json()
        if "error" in data:
            raise Exception("Invalid Zenobase credentials")
        self.access_token = data["access_token"]
        self.client_id = data["client_id"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _request(self, method, endpoint, data=None, headers={}):
        url = self.HOST + endpoint
        headers["Authorization"] = "Bearer {}".format(self.access_token)
        headers["Content-Type"] = "application/json"
        args = [url]
        kwargs = {"data": json.dumps(data), "headers": headers}
        r = method(*args, **kwargs)
        if not (200 <= r.status_code < 300):
            raise Exception("Status code was not 2xx: {}".format(r))

        if "content-type" in r.headers:
            if "application/json" in r.headers["content-type"]:
                return r.json()
        return r.text

    def _get(self, *args, **kwargs):
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request(requests.post, *args, **kwargs)

    def _delete(self, *args, **kwargs):
        return self._request(requests.delete, *args, **kwargs)

    def list_buckets(self, offset=0, limit=100):
        """Limit breaks above 100"""
        # TODO: If limit > 100, do multiple fetches
        if limit > 100:
            raise Exception("Zenobase can't handle limits over 100")
        return self._get("/users/{}/buckets/?order=label&offset={}&limit={}".format(self.client_id, offset, limit))

    def get_bucket(self, bucket_id):
        return self._get("/buckets/{}".format(bucket_id))

    def create_bucket(self, label, description=""):
        if not 1 <= len(label) <= 20:
            raise Exception("Bucket name must be 1-20 chars and can only contain [a-zA-Z0-9-_ ]")
        return self._post("/buckets/", data={"label": label, "description": description})

    def create_or_get_bucket(self, label, description=""):
        data = self.list_buckets()
        for bucket in data["buckets"]:
            if bucket["label"] == label:
                return bucket
        return self.create_bucket(label, description=description)

    def delete_bucket(self, bucket_id):
        self._delete("/buckets/{}".format(bucket_id))

    def list_events(self, bucket_id):
        return self._get("/buckets/{}/".format(bucket_id))

    @staticmethod
    def _bucket_id_from_bucket_or_id(bucket_or_bucket_id):
        assert isinstance(bucket_or_bucket_id, str) or isinstance(bucket_or_bucket_id, dict)
        if isinstance(bucket_or_bucket_id, str):
            bucket_id = bucket_or_bucket_id
        else:  # if isinstance(bucket_or_bucket_id, dict):
            if "@id" in bucket_or_bucket_id:
                bucket_id = bucket_or_bucket_id["@id"]
            else:
                raise Exception("@id field was not in the bucket dict, are you sure you passed a bucket?")
        return bucket_id

    def create_event(self, bucket_or_bucket_id, event):
        assert isinstance(event, ZenobaseEvent) or isinstance(event, dict)
        bucket_id = self._bucket_id_from_bucket_or_id(bucket_or_bucket_id)
        return self._post("/buckets/{}/".format(bucket_id), data=event)

    def create_events(self, bucket_or_bucket_id, events):
        assert isinstance(events, list)
        bucket_id = self._bucket_id_from_bucket_or_id(bucket_or_bucket_id)
        for event in events:
            assert isinstance(event, ZenobaseEvent) or isinstance(event, dict)
        return self._post("/buckets/"+bucket_id+"/", data={"events": events})

    def close(self):
        return self._delete("/authorizations/"+self.access_token)
