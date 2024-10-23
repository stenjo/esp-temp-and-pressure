import unittest
from Clock import Clock

class MockMatrix:
    def __init__(self):
        self.output = ""
        self.write_called = False

    def write(self, text, update):
        self.output = text
        self.write_called = True

class TestClock(unittest.TestCase):

    def setUp(self):
        self.matrix = MockMatrix()
        self.clock = Clock(15)

    def test_display_every_15_seconds(self):
        self.clock.set_test_time((0, 0, 0, 12, 0, 15, 0, 0))  # Mock time at 15th second
        self.assertTrue(self.clock.display(self.matrix))
        
        self.clock.set_test_time((0, 0, 0, 12, 0, 30, 0, 0))  # Mock time at 30th second
        self.assertTrue(self.clock.display(self.matrix))
        
        self.clock.set_test_time((0, 0, 0, 12, 0, 45, 0, 0))  # Mock time at 45th second
        self.assertTrue(self.clock.display(self.matrix))
        
    def test_display_only_when_seconds_change(self):
        self.clock.set_test_time((0, 0, 0, 13, 0, 2, 0, 0))  # Mock time at 45th second
        self.assertFalse(self.clock.display(self.matrix))
        self.assertEqual(self.matrix.output, "13:00")  # Should display hour:min with a space
        
        # Reset write_called flag
        self.matrix.write_called = False
  
        self.assertFalse(self.clock.display(self.matrix))
        self.assertFalse(self.matrix.write_called, "write() should not be called at 1st second")

        

    def test_display_even_odd_seconds(self):
        self.clock.set_test_time((0, 0, 0, 12, 0, 13, 0, 0))  # 14th second
        self.assertFalse(self.clock.display(self.matrix))
        self.assertEqual(self.matrix.output, "12 00")  # Should display hour:min with a space
        
        self.clock.set_test_time((0, 0, 0, 12, 0, 14, 0, 0))  # 14th second
        self.assertFalse(self.clock.display(self.matrix))
        self.assertEqual(self.matrix.output, "12:00")  # Should display hour:min without a space
        
        self.clock.set_test_time((0, 0, 0, 12, 0, 16, 0, 0))  # 16th second
        self.assertFalse(self.clock.display(self.matrix))
        self.assertEqual(self.matrix.output, "12:00")  # Should display hour:min without a space

        self.clock.set_test_time((0, 0, 0, 12, 0, 17, 0, 0))  # 17th second
        self.assertFalse(self.clock.display(self.matrix))
        self.assertEqual(self.matrix.output, "12 00")  # Should display hour:min with a space

if __name__ == '__main__':
    unittest.main()
    