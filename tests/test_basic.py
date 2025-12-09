import unittest


class TestSimple(unittest.TestCase):
    """Simple test to verify test framework is working"""
    
    def test_addition(self):
        """Test basic math - this should always pass"""
        self.assertEqual(1 + 1, 2)
    
    def test_string(self):
        """Test string comparison"""
        self.assertEqual("hello", "hello")
    
    def test_true(self):
        """Test boolean"""
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()