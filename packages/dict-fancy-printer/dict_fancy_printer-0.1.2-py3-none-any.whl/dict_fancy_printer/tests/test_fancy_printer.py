import unittest
from dict_fancy_printer.fancy_printer import FancyPrinter

class TestFancyPrinter(unittest.TestCase):

    def setUp(self):
        self.printer = FancyPrinter()

    def test_empty_dict(self):
        """Test that an empty dictionary is handled correctly"""
        result = self.printer({})
        # The output should be a string, not None or raise an exception
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_simple_dict(self):
        """Test with a simple dictionary"""
        test_dict = {"key1": "value1", "key2": "value2"}
        result = self.printer(test_dict)
        # Check that the output is a string and contains expected content
        self.assertIsInstance(result, str)
        self.assertIn("key1", result)
        self.assertIn("value1", result)

    def test_nested_dict(self):
        """Test with a nested dictionary"""
        test_dict = {
            "outer_key": {
                "inner_key": "inner_value"
            }
        }
        result = self.printer(test_dict)
        # Check that the output is a string and contains expected content
        self.assertIsInstance(result, str)
        self.assertIn("outer_key", result)
        self.assertIn("inner_key", result)

    def test_list_in_dict(self):
        """Test with a list inside a dictionary"""
        test_dict = {
            "list_key": ["item1", "item2"]
        }
        result = self.printer(test_dict)
        # Check that the output is a string and contains expected content
        self.assertIsInstance(result, str)
        self.assertIn("list_key", result)
        self.assertIn("item1", result)

    def test_private_keys(self):
        """Test handling of private keys (keys starting with underscore)"""
        test_dict = {
            "_private_key": "private_value",
            "public_key": "public_value"
        }
        # By default, private keys should be hidden
        result_default = self.printer(test_dict)
        self.assertNotIn("_private_key", result_default)

        # With show_private=True, private keys should be shown
        result_show_private = self.printer(test_dict, show_private=True)
        self.assertIn("_private_key", result_show_private)

    def test_key_triggers(self):
        """Test the key_triggers parameter"""
        # Create a dictionary with a key that will trigger color change
        # The key_trigger needs to be in something_hidden and item needs to be in dinput[key_triggers].keys()
        test_dict = {
            "_private": {"key1": "value1"},  # Private attribute that will be hidden by default
            "normal_key": "normal_value"
        }

        # With an empty key_triggers, the private key is hidden
        result_default = self.printer(test_dict, key_triggers="")
        self.assertNotIn("_private", result_default)

        # With show_private=True and key_triggers="_private", the key should be shown with different formatting
        result_with_trigger = self.printer(test_dict, key_triggers="_private", show_private=True)
        self.assertIn("_private", result_with_trigger)

        # The results should be different because in one case the private key is hidden and in another it's shown
        self.assertNotEqual(result_default, result_with_trigger)

if __name__ == "__main__":
    unittest.main()
