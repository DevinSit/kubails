import logging
from typing import List
from kubails.utils.service_helpers import call_command, get_command_output


logger = logging.getLogger(__name__)


class Git:
    def __init__(self):
        self.base_command = ["git"]

    def fetch(self, remote: str, prune: bool = False, unshallow: bool = False) -> bool:
        command = self.base_command + ["fetch", remote]

        if prune:
            command.append("--prune")

        if unshallow:
            command.append("--unshallow")

        return call_command(command)

    def get_remote_branches(self) -> List[str]:
        command = self.base_command + ["branch", "-r"]
        result = get_command_output(command)

        cleaned_branches = list(map(lambda x: x.strip().lower().replace("origin/", ""), result.split("\n")))
        filtered_branches = list(filter(None, cleaned_branches))

        return sorted(filtered_branches)

    def folder_changed(self, folder: str, current_branch: str, since_commit: str) -> bool:
        # Need the full git history to diff commits.
        self.fetch("origin", prune=True)
        self.fetch("origin", prune=True, unshallow=True)

        # Need to checkout the current_branch, otherwise it doesn't exist for the diff command.
        call_command(self.base_command + ["checkout", current_branch])

        command = self.base_command + ["diff", "--quiet", current_branch, since_commit, "--", folder]

        # If the command is successful, then that means there _no_ changes.
        # But since we want to know if the folder _did_ change, we have to invert the result.
        return not call_command(command)

    def get_commit_timestamp(self, commit_sha: str) -> int:
        # Note: "--format=%ct" gets the timestamp as a Unix epoch timestamp.
        # Makes it easier for sorting.
        command = self.base_command + ["show", "--quiet", "-s", "--format=%ct", commit_sha]

        output = get_command_output(command)

        # If the commit_sha isn't a valid commit, then the output will be blank. Return 0 instead.
        return int(output) if output else 0
