import pytz
from tzlocal import get_localzone


def fmt_datetime(dt, timezone=str(get_localzone())):
    tz = pytz.timezone(timezone)
    dt = dt.astimezone(tz) if dt.tzinfo else tz.localize(dt)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.000%z')
