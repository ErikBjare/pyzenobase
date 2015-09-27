import sys
import json
from datetime import datetime

from pyzenobase import ZenobaseAPI

if len(sys.argv) == 3:
    _, username, password, *_ = sys.argv
else:
    raise Exception("Could not parse username and password, too few or many arguments")

output_filename = "zenobase-dump-{}-{}.json".format(username, datetime.now().isoformat().split(".")[0])
print(output_filename)

with ZenobaseAPI(username, password) as zapi:
    # Buckets object below doesn't contain bucket data, only metadata.
    buckets = zapi.list_buckets(limit=100)["buckets"]
    print("Fetching {} buckets...".format(len(buckets)))

    for bucket in buckets:
        b_id, b_name = bucket["@id"], bucket["label"]
        print("Dumping bucket with id '{}' and label '{}'".format(b_id, b_name))
        events = zapi.list_events(b_id)["events"]
        bucket["events"] = events

with open(output_filename, "w+") as f:
    data = json.dumps(buckets)
    f.write(data)

print("Wrote result to {}".format(output_filename))
