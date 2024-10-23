import time

class Clock:
    
    lastSec = None
    interval = None
    
    def __init__(self, interval=None):
        self.interval = interval
        self._test_time = None  # For testing purposes

    def set_test_time(self, test_time):
        self._test_time = test_time

    def display(self, matrix):
        current_time = self._test_time if self._test_time else time.localtime()
        (_, _, _, hour, min, sec, _, _) = current_time
        
        if sec % self.interval == 0:
            self.lastSec = sec
            return True
        
        if sec is not self.lastSec:
            if sec % 2 == 0:
                matrix.write("{:02}:{:02}".format(hour, min), True)
            else:
                matrix.write("{:02} {:02}".format(hour, min), True)
        self.lastSec = sec
        return False