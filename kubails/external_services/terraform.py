import click
import logging
import os
from functools import reduce
from numbers import Number
from typing import Any, Callable, Dict, List
from kubails.utils.service_helpers import call_command, get_command_output


logger = logging.getLogger(__name__)

TERRAFORM_FOLDER = "terraform"


class Terraform:
    def __init__(self, variables: Dict[str, Any] = {}, root_folder: str = ".") -> None:
        self.root_folder = root_folder
        self.variables = variables
        self.base_command = ["terraform"]

    def init(self) -> bool:
        return self.run_command("init")

    def deploy(self) -> bool:
        return self.run_command("apply")

    def destroy(self) -> bool:
        state = self.get_state()
        state_without_kms = list(filter(lambda x: "module.kms" not in x, state))

        targets = list(map(lambda x: "-target={}".format(x), state_without_kms))

        if not targets:
            logger.info("Not destroying KMS keys. No other state to destroy. Exiting.")
            return True
        else:
            logger.info("Destroying infrastructure...")
            return self.run_command("destroy", targets + ["-auto-approve"])

    def destroy_cluster(self) -> bool:
        return self.run_command("destroy", ["-target", "google_container_cluster.primary"])

    def cluster_deployed(self) -> bool:
        return reduce(lambda acc, state: acc or "module.cluster" in state, self.get_state(), False)

    def get_cluster_name(self) -> str:
        return self.get_output("cluster_name")

    def get_public_ip(self) -> str:
        return self.get_output("ingress_ip")

    def get_name_servers(self) -> str:
        return self.get_output("dns_name_servers")

    def get_kms_key_name(self) -> str:
        return self.get_output("secrets_key_name")

    def get_kms_key_ring_name(self) -> str:
        return self.get_output("secrets_key_ring_name")

    def get_state(self) -> List[str]:
        get_state_command = self.base_command + ["state", "list"]
        return self._run_terraform_command(get_state_command, call_function=get_command_output).split("\n")

    def get_output(self, output: str) -> str:
        command = self.base_command + ["output", output]
        result = self._run_terraform_command(command, get_command_output)

        if not result:
            logger.error(
                "Terraform output '{}' doesn't exist. "
                "Has the infrastructure been deployed?".format(output)
            )

            raise click.Abort()

        return result

    def run_command(self, subcommand: str, arguments: List[str] = [], with_vars=True) -> bool:
        command = self.base_command + [subcommand]

        if self.variables and with_vars:
            command.extend(self._convert_config_to_var_options(self.variables))

        command.extend(arguments)
        return self._run_terraform_command(command)

    def _run_terraform_command(
        self,
        command: List[str],
        call_function: Callable[..., Any] = call_command
    ) -> Any:
        """
        Since some Terraform commands don't take a folder as an argument, we have to
        make sure that all commands are run inside the 'terraform' folder.
        """
        current_dir = os.getcwd()
        os.chdir(os.path.join(self.root_folder, TERRAFORM_FOLDER))

        result = call_function(command, shell=True)
        os.chdir(current_dir)

        return result

    def _convert_config_to_var_options(self, config: Dict[str, Any]) -> List[str]:
        var_options = []

        for key, value in config.items():
            var_options.append("-var")
            var_options.append("'{}={}'".format(key, self._stringify_value(value)))

        return var_options

    def _stringify_value(self, value: Any) -> str:
        if isinstance(value, dict):
            return self._stringify_dict(value)
        elif isinstance(value, list):
            return self._stringify_list(value)
        elif isinstance(value, bool):
            # Terraform only interprets 'true' or 'false', not 'True' or 'False';
            # thus, the string needs to be downcased.
            return "\"{}\"".format(str(value).lower())
        elif isinstance(value, str) or isinstance(value, Number):
            return "\"{}\"".format(value)
        elif value is None:
            return "\"\""
        else:
            raise ValueError("Value {} is not a string, bool, number, list, or dict.".format(value))

    def _stringify_dict(self, dict_to_convert: Dict[str, Any]) -> str:
        return "{{{}}}".format(reduce(
            lambda acc, pair: "{},{}={}".format(acc, pair[0], self._stringify_value(pair[1])),
            dict_to_convert.items(),
            ""
        )[1:])  # Remove the (useless) leading comma

    def _stringify_list(self, list_to_convert: List[str]) -> str:
        return "[{}]".format(reduce(
            lambda acc, item: "{},{}".format(acc, self._stringify_value(item)),
            list_to_convert,
            ""
        )[1:])  # Remove the (useless) leading comma
