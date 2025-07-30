import unittest
from dict_fancy_printer.functions import fancy_dict, print_fancy_dict

class TestFunctions(unittest.TestCase):

    def test_fancy_dict(self):
        """Test the fancy_dict function"""
        test_dict = {"key1": "value1", "key2": "value2"}
        result = fancy_dict(test_dict)
        # Check that the output is a string and contains expected content
        self.assertIsInstance(result, str)
        self.assertIn("key1", result)
        self.assertIn("value1", result)

    def test_print_fancy_dict(self):
        """Test the print_fancy_dict function"""
        test_dict = {"key1": "value1"}

        # Capture stdout to check printed output
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            print_fancy_dict(test_dict)

        output = f.getvalue()
        # Check that the output contains expected content
        self.assertIn("key1", output)
        self.assertIn("value1", output)

if __name__ == "__main__":
    unittest.main()