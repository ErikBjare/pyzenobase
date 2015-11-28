import sys
import json
from datetime import datetime

from pyzenobase import ZenobaseAPI


# Save buckets separately instead of in one big file
SAVE_SEPARATELY = False


def _save_to_file(obj, filename: str):
    print(" -> Saving as '{}'".format(filename))
    with open(filename, "w+") as f:
        data = json.dumps(obj)
        f.write(data)
    print(" <- Saved successfully (length {})".format(len(data)))

def _build_filename(username, label):
    return "zenobase-dump-{}-{}-{}.json".format(username, label, datetime.now().isoformat().split(".")[0])


def save_bucket_to_file(bucket: dict):
    filename = _build_filename(bucket["username"], bucket["label"])
    _save_to_file(bucket, filename)

def save_buckets_to_file(buckets: dict):
    filename = _build_filename(buckets[0]["username"], "all")
    _save_to_file(buckets, filename)


def main(username: str, password: str):
    with ZenobaseAPI(username, password) as zapi:
        # Buckets object below doesn't contain bucket data, only metadata.
        # Actual events are fetched and inserted in the for-loop that follows.
        buckets = zapi.list_buckets(limit=100)["buckets"]
        print("Fetching {} buckets...".format(len(buckets)))

        for i, bucket in enumerate(buckets):
            b_id, b_name = bucket["@id"], bucket["label"]
            bucket["username"] = username
            print(" -> Fetching bucket {} with label '{}' (id: '{}')".format(i+1, b_name, b_id))
            events = zapi.list_events(b_id)["events"]
            bucket["events"] = events
            print(" <- Fetched successfully")

            if SAVE_SEPARATELY:
                save_bucket_to_file(bucket)

            print("{}/{} complete".format(i+1, len(buckets)))

    if not SAVE_SEPARATELY:
        save_buckets_to_file(buckets)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        _, username, password, *_ = sys.argv
    else:
        raise Exception("Could not parse username and password, too few or many arguments")

    main(username, password)

