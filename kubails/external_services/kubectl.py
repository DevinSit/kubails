import logging
from typing import List
from kubails.utils.service_helpers import call_command, get_command_output


logger = logging.getLogger(__name__)


class Kubectl:
    def __init__(self):
        self.base_command = ["kubectl"]

    def deploy(self, manifest_location, recursive=False) -> bool:
        # NOTE: This is called 'deploy' instead of 'apply' because 'apply' is a reserved word.
        # I know, that doesn't really matter since this is a namespaced function, but whatever.

        command = self.base_command + ["apply"]
        command = command + ["--recursive"] if recursive else command
        command += ["-f", manifest_location]

        return call_command(command)

    def create_cluster_role_binding(self, name: str, role: str, user: str) -> bool:
        command = self.base_command + [
            "create", "clusterrolebinding", name,
            "--clusterrole", role,
            "--user", user
        ]

        return call_command(command)

    def get_namespaces(self, labels: List[str] = []) -> List[str]:
        command = self.base_command + ["get", "namespaces", "-o", "'name'"]

        for label in labels:
            command.extend(["-l", label])

        result = get_command_output(command, shell=True)

        cleaned_namespaces = list(map(lambda x: x.strip().lower().replace("namespace/", ""), result.split("\n")))
        filtered_namespaces = list(filter(None, cleaned_namespaces))
        return sorted(filtered_namespaces)

    def create_namespace(self, name: str, label: str = "") -> bool:
        result = True

        create_command = self.base_command + ["create", "namespace", name]
        result = result and call_command(create_command)

        if label:
            label_command = self.base_command + ["label", "namespace", name, label]
            result = result and call_command(label_command, shell=True)

        return result

    def delete_namespace(self, namespace: str) -> bool:
        command = self.base_command + ["delete", "namespace", namespace]
        return call_command(command)

    def create_secret_from_file(
        self, name: str, secret_file: str, namespace: str,
        secret_type: str = "generic", is_env_file: bool = False
    ) -> bool:
        from_option = "--from-env-file" if is_env_file else "--from-file"

        command = self.base_command + [
            "create", "secret", secret_type, name,
            "--namespace", namespace,
            from_option, secret_file
        ]

        return call_command(command)

    def delete_secret(self, name: str, namespace: str) -> bool:
        command = self.base_command + ["delete", "secret", name, "--namespace", namespace]
        return call_command(command)
