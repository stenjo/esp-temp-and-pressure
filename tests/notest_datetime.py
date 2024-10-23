import unittest
import sys
import os
custom_datetime_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'lib', 'micropython', 'lib', 'micropython-lib', 'python-stdlib', 'datetime')
sys.path.insert(0, custom_datetime_path)

from datetime import datetime,timezone, timedelta

class TestDatetime(unittest.TestCase):
    
    def test_strftime(self):
        ts = datetime(2023, 10, 22, 9, 18, 59)
        assert ts.strftime("%d/%m") == "22/10"
        assert ts.strftime(' kl. %H:%M') == " kl. 09:18"
        assert ts.strftime('%Y-%y') == "2023-23"
        assert ts.strftime("%d/%m/%Y, %H:%M:%S") == "22/10/2023, 09:18:59"
        
    def test_now(self):
        assert datetime.now(timezone.utc).year == datetime.datetime.now(datetime.timezone.utc).year
        
    def test_timedelta(self):
        today = datetime(2023,10,23)
        tomorrow = datetime(2023,10,24)
        assert today + timedelta(1) == tomorrow

    def test_timezone(self):
        _today = datetime.datetime(2023,10,23,10,12).replace(tzinfo=datetime.timezone.utc)
        today = datetime(2023,10,23,10,12).replace(tzinfo=timezone.utc)
        assert today.hour == _today.hour