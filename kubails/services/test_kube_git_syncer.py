from parameterized import parameterized
from unittest import TestCase
from . import kube_git_syncer


class TestKubeGitSyncer(TestCase):
    @parameterized.expand([
        # One unused namespace.
        [["a1"], ["a1", "b2"], ["b2"]],

        # No unused namespaces.
        [["a1", "b2"], ["a1", "b2"], []],

        # Remote branches are sanitized to match namespace naming conventino.
        [["test/A-1"], ["test-a-1", "thing-b-2"], ["thing-b-2"]]
    ])
    def test_can_get_unused_namespaces(self, remote_branches, existing_namespaces, expected):
        result = kube_git_syncer._get_unused_namespaces(remote_branches, existing_namespaces)
        self.assertEqual(result, expected)
