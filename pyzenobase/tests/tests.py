#!/usr/bin/python3

import time
import json
from pprint import pprint
import unittest
from random import randint

import requests

from pyzenobase import *

class ZenobaseTests(unittest.TestCase):
    def setUp(self):
        with open("pwd_zenobase.txt") as f:
            username, password = f.read().split("\n")[:2]
        self.zapi = ZenobaseAPI(username, password)

        bucket = self.zapi.create_or_get_bucket("Test - PyZenobaseAPI", description="This bucket is used by PyZenobaseAPI for testing.")
        self.bucket_id = bucket["@id"]

    def tearDown(self):
        pass

    def _test_bucket(self):
        buckets = self.zapi.list_buckets()
        n_buckets = buckets["total"]
        data = self.zapi.create_bucket("Test bucket", description="This bucket is for testing.")
        self.assertTrue(n_buckets+1 == self.zapi.list_buckets()["total"])
        self.zapi.delete_bucket(data["@id"])
        self.assertTrue(n_buckets == self.zapi.list_buckets()["total"])
    
    def test_bucket(self):
        data = self.zapi.create_bucket("Test bucket", description="This bucket is for testing.")
        self.zapi.delete_bucket(data["@id"])

    def test_event(self):
        event = ZenobaseEvent({"timestamp": "2014-09-06T19:35:00.000+02:00", "rating": randint(0, 100)})
        self.zapi.create_event(self.bucket_id, event)
        pprint(self.zapi.list_events(self.bucket_id))
        

if __name__ == "__main__":
    unittest.main()
