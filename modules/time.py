from utime import *
from micropython import const

_TS_YEAR = const(0)
_TS_MON = const(1)
_TS_MDAY = const(2)
_TS_HOUR = const(3)
_TS_MIN = const(4)
_TS_SEC = const(5)
_TS_WDAY = const(6)
_TS_YDAY = const(7)
_TS_ISDST = const(8)

_WDAY = const(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))
_MDAY = const(
    (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
)


def strftime(datefmt, ts):
    from io import StringIO

    fmtsp = False
    ftime = StringIO()
    for k in datefmt:
        if fmtsp:
            if k == "a":
                ftime.write(_WDAY[ts[_TS_WDAY]][0:3])
            elif k == "A":
                ftime.write(_WDAY[ts[_TS_WDAY]])
            elif k == "b":
                ftime.write(_MDAY[ts[_TS_MON] - 1][0:3])
            elif k == "B":
                ftime.write(_MDAY[ts[_TS_MON] - 1])
            elif k == "d":
                ftime.write("%02d" % ts[_TS_MDAY])
            elif k == "H":
                ftime.write("%02d" % ts[_TS_HOUR])
            elif k == "I":
                ftime.write("%02d" % (ts[_TS_HOUR] % 12))
            elif k == "j":
                ftime.write("%03d" % ts[_TS_YDAY])
            elif k == "m":
                ftime.write("%02d" % ts[_TS_MON])
            elif k == "M":
                ftime.write("%02d" % ts[_TS_MIN])
            elif k == "P":
                ftime.write("AM" if ts[_TS_HOUR] < 12 else "PM")
            elif k == "S":
                ftime.write("%02d" % ts[_TS_SEC])
            elif k == "w":
                ftime.write(str(ts[_TS_WDAY]))
            elif k == "y":
                ftime.write("%02d" % (ts[_TS_YEAR] % 100))
            elif k == "Y":
                ftime.write(str(ts[_TS_YEAR]))
            else:
                ftime.write(k)
            fmtsp = False
        elif k == "%":
            fmtsp = True
        else:
            ftime.write(k)
    val = ftime.getvalue()
    ftime.close()
    return val

################################################################
# Function time.localtime()
#
# Returns the local time for Norway with DST
#
# Credit to @steka for the code https://github.com/orgs/micropython/discussions/11173#discussioncomment-7524615
#

def localtime(secs: int | None = None) -> tuple[int, int, int, int, int, int, int, int]:
    """Returns Norwegian local time.

    According to [Wikipedia](https://en.wikipedia.org/wiki/Time_in_Norway)
    does Norway observe daylight saving time
    from: the last Sunday in March (02:00 CET)
    to:   the last Sunday in October (03:00 CEST)
    """

    def last_sunday(year: int, month: int, hour: int, minute: int) -> int:
        """Get the time of the last sunday of the month
        It returns an integer which is the number of seconds since Jan 1, 2000, just like mktime().
        """

        # Get the UTC time of the last day of the month
        seconds = mktime((year, month + 1, 0, hour, minute, 0, None, None))

        # Calculate the offset to the last sunday of the month
        # (year, month, mday, hour, minute, second, weekday, yearday) = gmtime(seconds)
        # offset = (weekday + 1) % 7
        tpl = gmtime(seconds)
        offset = (tpl[6] + 1) % 7

        # Return the time of the last sunday of the month
        return mktime((year, month, tpl[2] - offset, hour, minute, tpl[5], None, None))

    utc = gmtime(secs)

    # Find start date for daylight saving, i.e. last Sunday in March (01:00 UTC)
    start_secs = last_sunday(year=utc[0], month=3, hour=1, minute=0)

    # Find stop date for daylight saving, i.e. last Sunday in October (01:00 UTC)
    stop_secs = last_sunday(year=utc[0], month=10, hour=1, minute=0)

    utc_secs = mktime(utc)
    if utc_secs >= start_secs and utc_secs < stop_secs:
        delta_secs = 2 * 60 * 60  # Norwegian summer time (CEST or UTC + 2h)
    else:
        delta_secs = 1 * 60 * 60  # Norwegian normal time (CET or UTC + 1h)

    return gmtime(utc_secs + delta_secs)

