from parameterized import parameterized
from unittest import TestCase
from . import dependency_checker


dependencies_whitelist = ["gcloud",  "terraform"]


class MockClass:
    def __init__(self):
        self.terraform = {}
        self.gcloud = {}
        self.not_a_service = {}

    def mock_method(self):
        self.gcloud.authenticate_cluster()
        self.not_a_service.do_a_thing()

    def mock_method_with_private_calls(self):
        self._mock_private_method()
        self.gcloud.authenticate_cluster()

    def mock_method_with_nested_private_calls(self):
        self._mock_private_method_with_private_method()

    def _mock_private_method(self):
        self.terraform.get_cluster_name()

    def _mock_private_method_with_private_method(self):
        self._mock_private_method()


class TestTerraform(TestCase):
    @parameterized.expand([
        # Case 1: Method with just direct service calls.
        (MockClass, MockClass.mock_method, dependencies_whitelist, ["gcloud"]),

        # Case 2: Method with service calls and private method calls.
        (MockClass, MockClass.mock_method_with_private_calls, dependencies_whitelist, ["gcloud", "terraform"]),

        # Case 3: Method with nested private method calls.
        (MockClass, MockClass.mock_method_with_nested_private_calls, dependencies_whitelist, ["terraform"])
    ])
    def test_can_get_method_dependencies(self, cls, func, whitelist, expected_result):
        result = dependency_checker._get_method_dependencies(cls, func, whitelist)
        self.assertEqual(result, expected_result)
