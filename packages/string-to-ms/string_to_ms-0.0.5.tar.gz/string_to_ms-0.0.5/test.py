import unittest

from string_to_ms import ms

class TestMS(unittest.TestCase):

    def test_ms(self):
        self.assertEqual(ms(12345), "12.35 Seconds", "Should be 12.35 Seconds")

    def test_ms_no_decimal(self):
        self.assertEqual(ms(12345, False) , "12 Seconds", "Should be 12 Seconds")

    def test_no_unit(self):
        self.assertRaises(Exception, ms, "12345")
        self.assertRaises(Exception, ms, "ms")



if __name__ == '__main__':
    unittest.main()