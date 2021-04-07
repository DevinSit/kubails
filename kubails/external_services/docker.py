import logging
import os
from typing import List
from kubails.utils.service_helpers import call_command


logger = logging.getLogger(__name__)


class Docker:
    def __init__(self):
        self.base_command = ["docker"]

    def build(
        self,
        context: str,
        tags: List[str] = [],
        target_stage: str = None,
        cache_images: List[str] = [],
        branch: str = None,
    ) -> bool:
        command = self.base_command + [
            "build",
            # Need this in CI so that every log is output as its own line.
            "--progress=plain",
            # Need this otherwise the built images can't be used as cache images.
            # IDK why, I guess it's just a BuildKit thing.
            "--build-arg=BUILDKIT_INLINE_CACHE=1",
        ]

        if branch:
            command.extend(["--build-arg", "branch={}".format(branch)])

        if target_stage:
            command.extend(["--target", target_stage])

        for cache_image in cache_images:
            self.pull(cache_image)
            logger.info("Using {} as a cache image.".format(cache_image))
            command.extend(["--cache-from", cache_image])

        for tag in tags:
            command.extend(["-t", tag])

        command.append(context)

        # TECH DEBT: Because of a bug in BuildKit, if a registry mirror is specified during the build
        # command (i.e. in Cloud Build), then the pull of the Dockerfile's FROM image will fail
        # if the FROM image is not in the mirror. That is, if the image isn't in the mirror, BuildKit
        # won't try to pull from Docker Hub; it'll just explode.
        #
        # So we hack around this by manually pulling out the FROM images from the Dockerfile and
        # 'pre pull' them.
        #
        # VERY JANK. Just like BuildKit.
        self._pull_from_images(context)

        # Enable BuildKit to get 'faster' builds (supposedly).
        return call_command(command, env={"DOCKER_BUILDKIT": "1"})

    def pull(self, image: str) -> bool:
        command = self.base_command + ["pull", image]
        return call_command(command)

    def push(self, image: str) -> bool:
        command = self.base_command + ["push", image]
        return call_command(command)

    def _pull_from_images(self, context: str) -> bool:
        dockerfile = os.path.join(context, "Dockerfile")

        result = True

        with open(dockerfile, "r") as file:
            for line in file:
                if "FROM" in line:
                    image = line.split(" ")[1].strip()
                    result = result and self.pull(image)

        return result
