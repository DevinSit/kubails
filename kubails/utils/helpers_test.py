from unittest import TestCase


class CustomTestCase(TestCase):
    def assert_result_ok(self, result):
        self.assertEqual(result.exit_code, 0)

    def assert_result_bad(self, result):
        self.assertEqual(result.exit_code, 1)
