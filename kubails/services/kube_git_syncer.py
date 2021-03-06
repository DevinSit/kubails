import logging
from functools import reduce
from typing import List
from kubails.external_services import dependency_checker, git, kubectl
from kubails.utils.service_helpers import sanitize_name


logger = logging.getLogger(__name__)


@dependency_checker.check_dependencies()
class KubeGitSyncer:
    def __init__(self):
        self.git = git.Git()
        self.kubectl = kubectl.Kubectl()

    def cleanup_namespaces(self) -> bool:
        # Fetch and prune the branches so that the current repo copy is in
        # sync with the branches on origin
        self.git.fetch("origin", prune=True)
        self.git.fetch("origin", prune=True, unshallow=True)

        remote_branches = self.git.get_remote_branches()
        existing_namespaces = self.kubectl.get_namespaces(["kube-git-syncer=true"])

        unused_namespaces = _get_unused_namespaces(remote_branches, existing_namespaces)

        def cleanup_namespace(namespace: str) -> bool:
            result = self.kubectl.delete_namespace(namespace)

            if result:
                # Print the namespace so that it acts as output for the command.
                # This way, the cleanup command can be extended to do other things in user-land.
                # Note: Don't use the logger here, since we need the namespace to go to stdout
                # so that it can be captured in a variable.
                print(namespace)

            return result

        return reduce(
            lambda acc, namespace: acc and cleanup_namespace(namespace),
            unused_namespaces,
            True
        )


# Given the list of existing namespaces, this function determines which
# namespaces still exist for branches that have been deleted.
def _get_unused_namespaces(remote_branches: List[str], existing_namespaces: List[str]) -> List[str]:
    # Need to convert branch names to sanitized namespace names,
    # otherwise they'll always get cleaned up because they don't match.
    remote_branches = list(map(sanitize_name, remote_branches))
    unused_namespaces = [n for n in existing_namespaces if n not in remote_branches]

    logger.info("Remote Branches")
    logger.info(str(remote_branches))

    logger.info("Existing Namespaces")
    logger.info(str(existing_namespaces))

    logger.info("Unused Namespaces")
    logger.info(str(unused_namespaces))

    return unused_namespaces
