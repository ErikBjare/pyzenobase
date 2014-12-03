#!/usr/bin/python3

"""
    This is an example which grabs a spreadsheet (that follows a certain format) 
    from Google Docs and uploads the data into Zenobase.

    Example spreadsheet will be available at a later date.
"""

# TODO: Ability to only send updates (events with dates later than the latest in bucket)

import time
import datetime
import re
import pprint
import argparse
import logging

import requests
import gspread

import pyzenobase

class Lifelogger_to_Zenobase():
    def __init__(self, google_email, google_password, zenobase_username, zenobase_password):
        self.gc = gspread.login(google_email, google_password)
        logging.info("Authorization with Google successfull!")

        self.zapi = pyzenobase.ZenobaseAPI(zenobase_username, zenobase_password)
        self.ll = self.gc.open("Lifelogger")
        self.supplements_bucket = self.zapi.create_or_get_bucket("Supplements")

    def _create_events(self, bucket_id, events):
        logging.info("Uploading {} events...".format(len(events)))
        self.zapi.create_events(bucket_id, events)
        logging.debug("Done!".format(len(events)))

    def get_raw_table(self, sheetname):
        start = time.time()
        sheet = self.ll.worksheet(sheetname)
        raw_table = sheet.get_all_values()
        logging.debug("Took {}s to fetch worksheet '{}'".format(round(time.time()-start, 3), sheetname))
        return raw_table

    @staticmethod
    def get_dates(raw_table) -> "list of dates":
        """
            Goes through the first column of input table and 
            returns the first sequence of dates it finds.
        """
        dates = []
        found_first = False
        for i, dstr in enumerate([raw_table[i][0] for i in range(0, len(raw_table))]):
            if dstr:
                if len(dstr.split("/")) == 3:
                    d = datetime.datetime.strptime(dstr, '%m/%d/%Y')
                elif len(dstr.split("-")) == 3:
                    d = datetime.datetime.strptime(dstr, '%Y-%m-%d')
                else:
                    # Not necessarily an error, could just be a non-date cell
                    logging.debug("unknown date-format: {}".format(dstr))
                    continue
                dates.append(d)
                if not found_first:
                    found_first = True
                    logging.debug("Found first date: '{}' at i: {}".format(d.isoformat(), i))
            elif found_first:
                logging.debug("Last date: {}".format(d))
                break
        return dates


    def get_main(self) -> 'table[category: str][label: str][date: date]':
        """
            Returns a table with the above typesignature
        """

        raw_table = self.get_raw_table("M")
        categories = raw_table[0]
        labels = raw_table[1]
        dates = self.get_dates(raw_table)

        def next_cat_col(i):
            n = 1
            while True:
                if i+n > len(categories)-1:
                    return i
                if categories[i+n]:
                    return i+n
                n += 1

        def get_category_labels(i):
            end_col = next_cat_col(i)
            return zip(range(i, end_col), labels[i:end_col])

        def get_label_cells(category, label):
            ci = categories.index(category)
            i = labels.index(label, ci)
            cells = {}
            for j, d in enumerate(dates):
                cell = raw_table[j+2][i]
                if cell and cell != "#VALUE!":
                    cells[d] = cell
            return cells

        table = {}
        for i, cat in enumerate(categories):
            if not cat:
                continue
            table[cat] = {}
            for i, label in get_category_labels(i):
                table[cat][label] = get_label_cells(cat, label)

        return table


    """-------------------------------------------------------------------
    Here begins the extraction from the table and the export into Zenobase
    -------------------------------------------------------------------"""

    def create_streaks(self):
        table = self.get_main()
        bucket = self.zapi.create_or_get_bucket("Streaks")
        bucket_id = bucket["@id"]

        events = []
        for label in table["Streaks"]:
            for d in table["Streaks"][label]:
                val = table["Streaks"][label][d]
                mapping = {"TRUE": 1, "FALSE": -1}
                try:
                    state = mapping[val]
                except KeyError:
                    logging.warning("could not detect state of '{}'".format(val))
                    continue
                ts = pyzenobase.fmt_datetime(d, timezone="Europe/Stockholm")
                events.append(pyzenobase.ZenobaseEvent(
                        {"timestamp": ts, 
                         "count": state, 
                         "tag": [label, val]}))

        self._create_events(bucket_id, events)

    def create_daily_supps(self):
        raw_table = self.get_raw_table("D - Daily")
        labels = raw_table[0]
        dates = self.get_dates(raw_table)
        bucket_id = self.supplements_bucket["@id"]

        events = []
        for i, label in enumerate(labels):
            if not label:
                continue
            for j, d in enumerate(dates):
                if not raw_table[j+2][i]:
                    continue

                try:
                    weight = float(raw_table[j+2][i])
                except ValueError:
                    logging.warning("Invalid data '{}' (not a number) in cell: {}. Skipping..."
                            .format(raw_table[j+2][i], (j+2, i)))
                    continue

                events.append(pyzenobase.ZenobaseEvent(
                        {"timestamp": pyzenobase.fmt_datetime(d, timezone="Europe/Stockholm"),
                         "tag": [label, "daily"],
                         "weight": {
                             "@value": weight,
                             "unit": "mg"
                         }}))
        self._create_events(bucket_id, events)

    def create_timestamped_supps(self):
        # TODO: Support volume for drinks etc.
        raw_table = self.get_raw_table("D - Timestamped")
        dates = self.get_dates(raw_table)
        bucket_id = self.supplements_bucket["@id"]

        r_weight = re.compile("^[0-9]+\.?[0-9]*")
        r_unit = re.compile("mcg|ug|mg|g")

        events = []
        for i in range(1, len(raw_table[0]), 2):
            for j, d in enumerate(dates):
                try:
                    t = datetime.datetime.strptime(raw_table[j+1][i], "%H:%M:%S").time()
                except:
                    # Did not contain time
                    continue
                text = raw_table[j+1][i+1]
                
                try:
                    weight = float(r_weight.findall(text)[0])
                except ValueError:
                    logging.warning("Could not parse weight from '{}', skipping".format(text))
                    continue

                try:
                    unit = r_unit.findall(text)[0]
                except IndexError:
                    logging.warning("Could not parse unit from '{}', skipping".format(text))
                    continue

                # Convert units not supported by Zenobase
                if unit in ["mcg", "ug", "µg"]:
                    unit = "mg"
                    weight = weight/1000

                substance = text.split(" ")[1]
                event = pyzenobase.ZenobaseEvent(
                        {"timestamp": pyzenobase.fmt_datetime(datetime.datetime.combine(d, t), timezone="Europe/Stockholm"),
                         "tag": [substance, "timestamped"],
                         "weight": {
                             "@value": weight,
                             "unit": unit
                        }})
                events.append(event)
        self._create_events(bucket_id, events)

    def close(self):
        self.zapi.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    parser = argparse.ArgumentParser(description="Upload data from Lifelogger spreadsheet to Zenobase")
    parser.add_argument("google_email")
    parser.add_argument("google_password")
    parser.add_argument("zenobase_username")
    parser.add_argument("zenobase_password")
    args = parser.parse_args()

    create_streaks = input("Create streaks? (y/N): ") == "y"
    create_daily_supps = input("Create daily supplements? (y/N): ") == "y"
    create_timestamped_supps = input("Create timestamped supplements? (y/N): ") == "y"
    
    l2z = Lifelogger_to_Zenobase(args.google_email, args.google_password, args.zenobase_username, args.zenobase_password)

    if create_streaks:
        l2z.create_streaks()
    if create_daily_supps:
        l2z.create_daily_supps()
    if create_timestamped_supps:
        l2z.create_timestamped_supps()

    l2z.close()
