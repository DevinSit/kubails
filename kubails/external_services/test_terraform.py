from parameterized import parameterized
from unittest import TestCase
from . import terraform


class TestTerraform(TestCase):
    def setUp(self):
        self.terraform = terraform.Terraform()
        self.maxDiff = None

    @parameterized.expand([
        # Case 1: Boolean
        (True, "true"),

        # Case 2: String
        ("value", "value"),

        # Case 3: Number
        (3, "3"),

        # Case 4: Simple dict with string value
        ({"key": "value"}, "{key=\"value\"}"),

        # Case 5: Simple dict with list value
        ({"key": ["value"]}, "{key=[\"value\"]}"),

        # Case 6: Simple dict with number value
        ({"key": 3}, "{key=\"3\"}"),

        # Case 7: Simple dict with bool values
        ({"key": True, "key2": False}, "{key=\"true\",key2=\"false\"}"),

        # Case 8: Complex dict with multiple values
        (
            {"str": "value", "list": ["str", 3], "number": 3},
            "{str=\"value\",list=[\"str\",\"3\"],number=\"3\"}"
        ),

        # Case 9: Simple list with string value
        (["value"], "[\"value\"]"),

        # Case 10: Simple list with number value
        ([3], "[\"3\"]"),

        # Case 11: Simple list with dict value
        ([{"key": "value", "key2": "value2"}], "[{key=\"value\",key2=\"value2\"}]"),

        # Case 12: Complex list with multiple values
        (["value", 3, {"key": "value"}], "[\"value\",\"3\",{key=\"value\"}]"),

        # Case 13: Can handle null values
        ([None], "[\"\"]")
    ])
    def test_can_stringify_value(self, input_value, expected_string):
        string = self.terraform._stringify_value(input_value)
        self.assertEqual(string, expected_string)

    def test_can_not_stringify_value(self):
        with self.assertRaises(ValueError):
            self.terraform._stringify_value(self.terraform)
