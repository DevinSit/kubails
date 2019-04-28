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
