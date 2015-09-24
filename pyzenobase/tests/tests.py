#!/usr/bin/python3

import time
import json
from pprint import pprint
import unittest
from random import randint
import requests
from datetime import datetime, timezone

import pyzenobase
from pyzenobase import *

class ZenobaseTests(unittest.TestCase):
    def setUp(self):
        self.zapi = ZenobaseAPI()
        self.assertEqual(self.zapi.list_buckets()["total"], 0)
        bucket = self.zapi.create_or_get_bucket("Test - PyZenobaseAPI", description="This bucket is used by PyZenobaseAPI for testing.")
        time.sleep(1)
        self.assertEqual(self.zapi.list_buckets()["total"], 1)
        self.bucket_id = bucket["@id"]

    def test_create_event(self):
        events = self.zapi.list_events(self.bucket_id)["events"]
        self.assertEqual(len(events), 0)
        event = ZenobaseEvent({
            "timestamp": pyzenobase.fmt_datetime(datetime.now(timezone.utc), timezone="Europe/Stockholm"),
            "rating": randint(0, 100)
        })
        self.zapi.create_event(self.bucket_id, event)
        time.sleep(1)
        events = self.zapi.list_events(self.bucket_id)["events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["timestamp"], event["timestamp"])
        self.assertEqual(events[0]["rating"], event["rating"])

    def test_event_timestamp(self):
        event = ZenobaseEvent({"timestamp": datetime.now()})
        json.dumps(event)
        
        event = ZenobaseEvent({"timestamp": [datetime.now(), datetime.now()]})
        json.dumps(event)

        event = ZenobaseEvent({"timestamp": "s"})
        json.dumps(event)
        
        event = ZenobaseEvent({"timestamp": ["s1", "s2"]})
        json.dumps(event)
        
        event = ZenobaseEvent({"timestamp": ["s1", datetime.now()]})
        json.dumps(event)

        try:
            event = ZenobaseEvent({"timestamp": 12})
            self.fail()
        except TypeError:
            pass

    def test_with_stmt(self):
        close_called = [False]
        old_close = ZenobaseAPI.close

        def new_close(self):
            close_called[0] = not close_called[0]
            old_close(self)
        ZenobaseAPI.close = new_close

        with ZenobaseAPI() as zapi:
            pass

        ZenobaseAPI.close = old_close
        self.assertTrue(close_called[0])

    def tearDown(self):
        self.zapi.delete_bucket(self.bucket_id)
        self.zapi.close()


class ExampleTest(unittest.TestCase):
    def testExample(self):
        with ZenobaseAPI() as zapi:
            bucket = zapi.create_or_get_bucket("Test", description="Testing...")
            event = ZenobaseEvent({"timestamp": datetime.now(), "note": "Hello world!", "tag": ["test", "pyzenobase"]})
            zapi.create_event(bucket, event)


if __name__ == "__main__":
    unittest.main()

