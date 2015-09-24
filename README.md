PyZenobase
==========

[![Build Status](https://travis-ci.org/ErikBjare/pyzenobase.svg?branch=master)](https://travis-ci.org/ErikBjare/pyzenobase)

A small and simple (but helpful) library to aid in uploading and fetching data to/from [Zenobase](https://zenobase.com/).

## Installation
Install by using any of the following commands, prefix with `sudo` if necessary.
 - `pip3 install git+https://github.com/ErikBjare/pyzenobase.git`
 - `pip3 install .` after cloning into working directory
 - `python3 ./setup.py install` after cloning into working directory

## Examples & Usages
Check out the examples in the projects `./examples` directory. 
 
 - [Lifelogger Export](./examples/upload_lifelogger_spreadsheet/) - A script that turns a Google Docs spreadsheet into Zenobase data with support for logging daily supplements, timestamped supplements/drugs and habit streaks (deprecated).
 - [Battery Log Export](./examples/upload_battery_data_csv/) - Uploads battery data from a CSV file as exported by the Android app [Battery Log](https://play.google.com/store/apps/details?id=kr.hwangti.batterylog).

If you are looking for other uses, check the list here:

 - [Rescuetime Exporter](https://github.com/ErikBjare/rescuetime-exporter) - Exports RescueTime data at the highest resolution possible to a CSV file, comes with a `to_zenobase.py` script.

If you are using PyZenobase, please let me know by [sending an email](mailto:erik.bjareholt@gmail.com) so I can add it to this list!

## Documentation
Not yet available, but codebase is small so reading `./pyzenobase/main.py` should be enough to understand how to use it.
For info about the general Zenobase API, look [here](https://zenobase.com/#/api/).


### Example

Here is a simple example sending a single event to Zenobase.

    from pyzenobase import ZenobaseAPI, ZenobaseEvent

    USERNAME=""
    PASSWORD=""

    with ZenobaseAPI(USERNAME, PASSWORD) as zapi:
         bucket = zapi.create_or_get_bucket("Test", description="Testing...")
         event = ZenobaseEvent({"timestamp": datetime.now(), "note": "Hello world!", "tag": ["test", "pyzenobase"]})
         zapi.create_event(bucket, event)
        
        

