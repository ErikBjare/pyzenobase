#!/usr/bin/python3

import time
import json
from pprint import pprint
import unittest
from random import randint
import requests
import time

from pyzenobase import *

class ZenobaseTests(unittest.TestCase):
    def setUp(self):
        self.zapi = ZenobaseAPI()
        self.assertEqual(self.zapi.list_buckets()["total"], 0)
        bucket = self.zapi.create_or_get_bucket("Test - PyZenobaseAPI", description="This bucket is used by PyZenobaseAPI for testing.")
        time.sleep(1)
        self.assertEqual(self.zapi.list_buckets()["total"], 1)
        self.bucket_id = bucket["@id"]

    def test_event(self):
        events = self.zapi.list_events(self.bucket_id)["events"]
        self.assertEqual(len(events), 0)
        event = ZenobaseEvent({"timestamp": "2014-09-06T19:35:00.000+02:00", "rating": randint(0, 100)})
        self.zapi.create_event(self.bucket_id, event)
        time.sleep(1)
        events = self.zapi.list_events(self.bucket_id)["events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["timestamp"], event["timestamp"])
        self.assertEqual(events[0]["rating"], event["rating"])

    def tearDown(self):
        self.zapi.delete_bucket(self.bucket_id)
        self.zapi.close()

if __name__ == "__main__":
    unittest.main()
