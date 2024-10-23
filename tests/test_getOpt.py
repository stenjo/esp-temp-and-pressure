import sys
import unittest
from getopt import GetoptError

class TestGetOpt(unittest.TestCase):
    def test_getOpt(self):
        e = GetoptError("test")
        
        assert e.msg == "test"
        
if __name__ == '__main__':
    # Add the path to MicroPython in lib/micropython to sys.path
    sys.path.insert(0, 'lib')

    # Run the tests
    unittest.main()
