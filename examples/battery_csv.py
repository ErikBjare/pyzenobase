import csv
import argparse
from datetime import datetime

import pyzenobase
    
def upload_batterystats(filename, username, password, bucket_name="Battery - PyZenobase", bucket_desc="Uploaded using PyZenobase (http://github.com/ErikBjare/PyZenobase)"):

    zapi = pyzenobase.ZenobaseAPI(username, password)
    bucket = zapi.create_or_get_bucket(bucket_name, description=bucket_desc)
    bucket_id = bucket["@id"]

    with open("/home/erb/Dropbox/Logging/BatteryLog.csv", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        events = []
        for row in reader:
            events.append({header[i]: row[i] for i in range(len(header))})

        for event in events:
            # Transform data
            event["timestamp"] = pyzenobase.dt_to_timestamp(datetime.strptime(event.pop("datetime"), "%Y-%m-%d %H:%M:%S"), timezone="+01:00")
            event["tag"] = event.pop("status")
            event["percentage"] = float(event.pop("level"))
            event["temperature"] = {"@value": float(event.pop("temperature")), "unit": "C"}
            event.pop("voltage")

        for i, event in enumerate(events):
            zapi.create_event(bucket_id, pyzenobase.ZenobaseEvent(event))
            print("Created {}/{} events".format(i+1, len(events)))

    print("Done!")

if __name__ == "__main__":
    bucket_name = "Battery - Nexus 5"
    bucket_desc = "Logged with the Android app Battery Log (https://play.google.com/store/apps/details?id=kr.hwangti.batterylog). Uploaded using PyZenobase."

    parser = argparse.ArgumentParser(description='Upload batterystats')
    parser.add_argument("filename")
    parser.add_argument("username")
    parser.add_argument("password")

    args = parser.parse_args()

    upload_batterystats(args.filename, args.username, args.password)
