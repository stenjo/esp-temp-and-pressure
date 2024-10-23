
import sys
import os
import time as mod_time
import datetime as mod_datetime
from datetime import MAXYEAR, MINYEAR, datetime, date, time, timedelta, timezone, tzinfo
import unittest


# See localtz.patch
try:
    datetime.fromtimestamp(0)
    LOCALTZ = True
except NotImplementedError:
    LOCALTZ = False


if hasattr(datetime, "EPOCH"):
    EPOCH = datetime.EPOCH
else:
    EPOCH = datetime(*mod_time.gmtime(0)[:6], tzinfo=timezone.utc)


def eval_mod(s):
    return eval(s.replace("datetime.", "mod_datetime."))


class TestDateTime(unittest.TestCase):
    def test_strftime(self):
        
        assert datetime(2023, 12, 31).year == 2023
        assert datetime(2023, 12, 31).strftime("%Y-%m-%d") == "2023-12-31"
    
    
if __name__ == '__main__':
    # Run the tests
    unittest.main()