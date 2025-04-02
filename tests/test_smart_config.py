import unittest
import os
from src.lib.smart_config import Config, RangeConfig, EnumConfig, BoolDropdownConfig

class TestSmartConfig(unittest.TestCase):

    def setUp(self):
        """Set up a temporary config file for testing."""
        self.test_config_file = "/tmp/test_config.json"
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        self.config = Config(self.test_config_file)

    def tearDown(self):
        """Clean up the temporary config file."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)

    def test_add_and_save_config(self):
        """Test adding and saving a config item."""
        self.config.add("test_key", "test_value")
        self.assertEqual(self.config["test_key"], "test_value")

        # Ensure the value is saved to the file
        self.config.save()
        with open(self.test_config_file, "r") as f:
            data = f.read()
        self.assertIn("test_key", data)

    def test_range_config(self):
        """Test the RangeConfig class."""
        range_config = RangeConfig("Test Range", 0, 100, current=50)
        self.assertEqual(range_config["current"], 50)

        # Test updating the value
        range_config.parse_value(75)
        self.assertEqual(range_config["current"], 75)

        range_config.parse_value("75")
        self.assertEqual(range_config["current"], 75)

        # Test out-of-range value
        with self.assertRaises(ValueError):
            range_config.parse_value(150)

    def test_enum_config(self):
        """Test the EnumConfig class."""
        enum_config = EnumConfig("Test Enum", ["Option1", "Option2", "Option3"], current="Option2")
        self.assertEqual(enum_config["current"], "Option2")

        # Test updating the value
        enum_config.parse_value("Option3")
        self.assertEqual(enum_config["current"], "Option3")

        # Test invalid value
        with self.assertRaises(ValueError):
            enum_config.parse_value("InvalidOption")

    def test_bool_dropdown_config(self):
        """Test the BoolDropdownConfig class."""
        bool_config = BoolDropdownConfig("Test Bool", current=True)
        self.config.add("Test Bool", bool_config)
        self.assertTrue(bool_config.value())
        print(self.config.items())

        # Test updating the value
        bool_config.parse_value("False")
        self.assertFalse(bool_config.value())


    def test_as_html(self):
        """Test the as_html method."""
        self.config.add("test_key", "test_value")
        self.config.add("test_bool", True)
        html = self.config.as_html()
        self.assertIn('<label for="test_key">test_key</label>', html)
        self.assertIn('<input type="text" name="test_key" value=test_value>', html)
        self.assertIn('<input type="checkbox" name="test_bool" checked value=true', html)

    def test_update_config(self):
        """Test updating the config with new data."""
        self.config.add("test_key", "test_value")
        self.config.update({"test_key": "new_value", "new_key": "another_value"})
        self.assertEqual(self.config["test_key"], "new_value")
        self.assertEqual(self.config["new_key"], "another_value")


    def test_load_and_save(self):
        """Test loading and saving the config."""
        self.config.add("test_key", "test_value")
        self.config.add("test_range", RangeConfig("test_range", 0, 100, current=50))
        self.config.add("test_enum", EnumConfig("test_enum", ["Option1", "Option2"], current="Option1"))
        self.config.add("test_bool", BoolDropdownConfig("test_bool", current=True))
        self.config["test_range"].parse_value(75)
        self.config["test_enum"].parse_value("Option2")
        self.config["test_bool"].parse_value("False")
        self.assertEqual(self.config["test_range"]["current"], 75)
        self.assertEqual(self.config["test_enum"]["current"], "Option2")
        self.assertFalse(self.config["test_bool"].value())
        print(type(self.config["test_bool"]))
        print(self.config["test_bool"])
        import json
        print(json.dumps(self.config))
        print(json.dumps(self.config["test_bool"]))
        self.config.save()

        with open(self.test_config_file, "r") as f:
            data = f.read()
            print(data)

        # Create a new Config object and load the saved data
        new_config = Config(self.test_config_file)
        self.assertEqual(new_config["test_key"], "test_value")
        self.assertEqual(new_config["test_range"]["current"], 75)
        self.assertEqual(new_config["test_enum"]["current"], "Option2")
        self.assertFalse(new_config["test_bool"].value())

    def test_coercion(self):
        """Test coercion of values."""
        self.config.add("test_key", 123)
        self.config.add("test_range", RangeConfig("test_range", 0, 100, current=50))
        self.config.add("bool_dropdown", BoolDropdownConfig("bool_dropdown", current=True))
        self.config["test_range"].parse_value(75)
        self.assertEqual(self.config["test_key"], 123)
        self.assertEqual(self.config["test_range"]["current"], 75)
        self.assertEqual(self.config["test_range"], 75)
        self.assertTrue(self.config["bool_dropdown"].value())
        self.assertEqual(self.config["bool_dropdown"], True)
        self.config["bool_dropdown"].parse_value("False")
        self.assertFalse(self.config["bool_dropdown"].value())
        self.assertEqual(self.config["bool_dropdown"], False)

if __name__ == "__main__":
    unittest.main()