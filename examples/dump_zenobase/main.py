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
    buckets_meta = zapi.list_buckets(limit=50)["buckets"]
    print(len(buckets_meta))
    bucket_id_name_pair = map(lambda b: (b["@id"], b["label"]), buckets_meta)

    buckets = []
    for b_id, b_name in bucket_id_name_pair:
        print("Dumping bucket with id '{}' and label '{}'".format(b_id, b_name))
        buckets.append(zapi.get_bucket(b_id))

with open(output_filename, "w+") as f:
    data = json.dumps(buckets)
    f.write(data)

print("Wrote result to {}".format(output_filename))
