import logging
from typing import List
from kubails.utils.service_helpers import call_command


logger = logging.getLogger(__name__)


class Docker:
    def __init__(self):
        self.base_command = ["docker"]

    def build(self, context: str, tags: List[str] = [], cache_image: str = None, branch: str = None) -> bool:
        command = self.base_command + ["build"]

        for tag in tags:
            command.extend(["-t", tag])

        if cache_image:
            command.extend(["--cache-from", cache_image])

        if branch:
            command.extend(["--build-arg", "branch={}".format(branch)])

        command.append(context)

        if cache_image and not self.pull(cache_image):
            logger.info("No cache found for image {}.".format(cache_image))

        return call_command(command)

    def pull(self, image: str) -> bool:
        command = self.base_command + ["pull", image]
        return call_command(command)

    def push(self, image: str) -> bool:
        command = self.base_command + ["push", image]
        return call_command(command)
