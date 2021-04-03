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
        print()
        logger.info("Initializing Terraform...")
        print()

        # `init` needs to be run without vars, otherwise the google provider will throw:
        # `Error installing provider "google": exec: "getent": executable file not found in $PATH.`
        return self.run_command("init", with_vars=False)

    def deploy(self) -> bool:
        print()
        logger.info("Deploying Terraform infrastructure...")
        print()

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
        return reduce(
            lambda acc, state: acc or "module.cluster.google_container_cluster" in state,
            self.get_state(),
            False
        )

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
        command = self.base_command + ["output", "-json", output]
        result = self._run_terraform_command(command, get_command_output)

        if not result:
            logger.error(
                "Terraform output '{}' doesn't exist. "
                "Has the infrastructure been deployed?".format(output)
            )

            raise click.Abort()

        return result

    def run_command(self, subcommand: str, arguments: List[str] = [], with_vars=True) -> bool:
        command = self.base_command + [subcommand] + arguments
        var_options = self._convert_config_to_var_options(self.variables) if self.variables and with_vars else None

        return self._run_terraform_command(command, env_vars=var_options)

    def _run_terraform_command(
        self,
        command: List[str],
        call_function: Callable[..., Any] = call_command,
        env_vars: Dict[str, str] = None
    ) -> Any:
        """
        Runs a Terraform command.

        Since some Terraform commands don't take a folder as an argument, we have to
        make sure that all commands are run inside the 'terraform' folder.

        Note for @param env_vars:

            The default/empty value _must_ None. If the default/empty value is just an empty dict
            (or otherwise), then this can cause problems with commands expected normal environment
            variables.

            This is noted here: https://docs.python.org/2/library/subprocess.html#popen-constructor
            "If specified, env must provide any variables required for the program to execute."

            This first came up when trying to run `terraform init` with an empty dict.
            When installing the google provider, it would throw this error:
            "Error installing provider "google": exec: "getent": executable file not found in $PATH."

            This error is a direct result of providing an empty env dict and triggering a loss
            of other environment variables for commands.

            Whether or not this will affect other commands that need TF_VAR env variables is unknown at the moment.
        """
        current_dir = os.getcwd()
        os.chdir(os.path.join(self.root_folder, TERRAFORM_FOLDER))

        result = call_function(command, shell=True, env=env_vars)
        os.chdir(current_dir)

        return result

    def _convert_config_to_var_options(self, config: Dict[str, Any]) -> Dict[str, str]:
        var_options = {}

        for key, value in config.items():
            # We originally used '-var' options and just appended them to the Terraform command.
            #
            # However, Terraform 0.12 changed so that it would throw an error whenever it received
            # a '-var' option for an undeclared variable (i.e. it didn't exist in variables.tf).
            #
            # This is quite problematic for us since Kubails depends on being able to just dump
            # kubails.json to Terraform without worrying about what has been declared or not.
            #
            # As a result, we have switched to passing values using the "TF_VAR" env var method.
            #
            # This problem, and solution, are documented here: https://github.com/hashicorp/terraform/issues/22004.
            var_options["TF_VAR_{}".format(key)] = self._stringify_value(value)

        return var_options

    def _stringify_value(self, value: Any, top_level: bool = True) -> str:
        # (OK, this is really stupid, but I couldn't think of a better solution, so...)
        #
        # 'top_level' is a flag that indicates whether _stringify_value has been called recursively or not.
        #
        # The reason we need this is because Terraform 0.12 changed how '-var' and 'TF_VAR' args are passed.
        # Now, when it receives an arg like `-var '_project_name="name"'`, it interprets the double quotes literally.
        # This is noted here: https://www.terraform.io/docs/configuration/variables.html#complex-typed-values.
        #
        # That is, when interpolating the variable like `"${_project_name}-bucket"`, it literally outputs
        # `""name"-bucket"`, with the double quotes included. Obviously, this then breaks the parsing
        # of the whole string, since it will seem (to Terraform) to be multiple strings.
        #
        # However, this literal quoting only happens with non-map, non-list values. Because the values
        # in a list or map still need to be quoted properly... but it won't take those as literal quotes.
        #
        # See here for some valid Terraform 0.12 examples:
        # https://www.terraform.io/docs/configuration/variables.html#variables-on-the-command-line
        #
        # WHY it does this now, I have no clue.
        #
        # As such, when _stringify_value isn't called recursively (i.e. at 'top_level'), we _don't_ want
        # to wrap values in double quotes, but we _do_ when it _is_ called recursively (i.e. not at 'top_level').

        if isinstance(value, dict):
            return self._stringify_dict(value)
        elif isinstance(value, list):
            return self._stringify_list(value)
        elif isinstance(value, bool):
            # Terraform only interprets 'true' or 'false', not 'True' or 'False'; thus, it needs to be lowercase.
            stringified_value = str(value).lower()

            return "\"{}\"".format(stringified_value) if not top_level else stringified_value
        elif isinstance(value, str) or isinstance(value, Number):
            return "\"{}\"".format(value) if not top_level else "{}".format(value)
        elif value is None:
            return "\"\""
        else:
            raise ValueError("Value {} is not a string, bool, number, list, or dict.".format(value))

    def _stringify_dict(self, dict_to_convert: Dict[str, Any]) -> str:
        return "{{{}}}".format(reduce(
            lambda acc, pair: "{},{}={}".format(acc, pair[0], self._stringify_value(pair[1], top_level=False)),
            dict_to_convert.items(),
            ""
        )[1:])  # Remove the (useless) leading comma

    def _stringify_list(self, list_to_convert: List[str]) -> str:
        return "[{}]".format(reduce(
            lambda acc, item: "{},{}".format(acc, self._stringify_value(item, top_level=False)),
            list_to_convert,
            ""
        )[1:])  # Remove the (useless) leading comma
