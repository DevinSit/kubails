from parameterized import parameterized
from unittest import TestCase
from . import service_helpers


class TestServiceHelpers(TestCase):
    @parameterized.expand([
        # Everything is lower cased.
        ["ABC123", "abc123"],
        ["ABC-123", "abc-123"],

        # Special characters are replaced by hyphens.
        ["test/ABC-123", "test-abc-123"],
        ["t@e#s$t%a^l&l*t(h)e-t_h+i=n{g}s", "t-e-s-t-a-l-l-t-h-e-t-h-i-n-g-s"],
    ])
    def test_can_sanitize_name(self, name, expected):
        result = service_helpers.sanitize_name(name)
        self.assertEqual(result, expected)
