import logging
from functools import reduce
from typing import List
from kubails.external_services import git, kubectl


logger = logging.getLogger(__name__)


class KubeGitSyncer:
    def __init__(self):
        self.git = git.Git()
        self.kubectl = kubectl.Kubectl()

    def cleanup_namespaces(self) -> bool:
        # Fetch and prune the branches so that the current repo copy is in
        # sync with the branches on origin
        self.git.fetch("origin", prune=True)
        self.git.fetch("origin", prune=True, unshallow=True)

        unused_namespaces = self._get_unused_namespaces()

        return reduce(
            lambda acc, namespace: acc and self.kubectl.delete_namespace(namespace),
            unused_namespaces,
            True
        )

    def _get_unused_namespaces(self) -> List[str]:
        remote_branches = self.git.get_remote_branches()
        existing_namespaces = self.kubectl.get_namespaces(["kube-git-syncer=true"])
        unused_namespaces = [n for n in existing_namespaces if n not in remote_branches]

        logger.info("Remote Branches")
        logger.info(str(remote_branches))

        logger.info("Existing Namespaces")
        logger.info(str(existing_namespaces))

        logger.info("Unused Namespaces")
        logger.info(str(unused_namespaces))

        return unused_namespaces
