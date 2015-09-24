from datetime import datetime
from pyzenobase import fmt_datetime

_VALID_FIELDS = ["bits", "concentration", "count", "currency", "distance",
                 "distance/volume", "duration", "energy", "frequency", "height",
                 "humidity", "location", "moon", "note", "pace", "percentage",
                 "pressure", "rating", "resource", "sound", "source", "tag",
                 "temperature", "timestamp", "velocity", "volume", "weight"]


class ZenobaseEvent(dict):
    """
        Provides simple structure checking
    """
    def __init__(self, data):
        super(ZenobaseEvent, self).__init__(self)
        for field in data:
            assert field in _VALID_FIELDS
            self[field] = data[field]

        self.clean_data()

    def clean_data(self):
        """Ensures data is Zenobase compatible and patches it if possible,
        if cleaning is not possible it'll raise an appropriate exception"""

        # TODO: Do the same for duration/timedelta
        if "timestamp" in self:
            self._check_timestamp()
            if type(self["timestamp"]) == list:
                def datetime_to_string(dt):
                    return fmt_datetime(dt) if type(dt) == datetime else dt
                self["timestamp"] = list(map(datetime_to_string, self["timestamp"]))
            elif type(self["timestamp"]) == datetime:
                self["timestamp"] = fmt_datetime(self["timestamp"])

        # FIXME: Support list of volumes
        if "volume" in self:
            self["volume"]["unit"] = self["volume"]["unit"].replace("l", "L")

        # FIXME: Support list of weights
        if "weight" in self:
            # Zenobase uses "ug" for micrograms
            if self["weight"]["unit"] in ["mcg", "µg"]:
                self["weight"]["unit"] = "ug"

    def _check_timestamp(self):
        if not type(self["timestamp"]) in (str, datetime, list) and \
                (type(self["timestamp"]) != list or all(map(lambda x: type(x) in (str, datetime), self["timestamp"]))):
            raise TypeError("timestamp must be string, datetime or list of strings/datetimes")

