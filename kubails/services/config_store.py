import click
import json
import logging
import os
import operator
import traceback
from functools import reduce
from typing import Any, Dict, List, Union


logger = logging.getLogger(__name__)

CONFIG_FILE_NAME = "kubails.json"


class ConfigStore:
    def __init__(self, config: Dict[str, Any] = {}, config_file_name: str = CONFIG_FILE_NAME) -> None:
        if config:  # So that it doesn't go searching for config files during tests
            self.config = config
        else:
            self.config_file_name = config_file_name
            self.config_dir = self._search_for_file_dir(self.config_file_name)
            self.config_path = os.path.join(self.config_dir, self.config_file_name)

            self.config = self._open_config()

        self._parse_config(self.config)

    def get_config(self) -> Dict[str, Any]:
        return self.config

    def get_flattened_config(self) -> Dict[str, Any]:
        """
        Terraform variable config files (i.e. .tfvars files) can only have maps that are
        one level deep. The Kubails config has more than one level of maps.
        Hence, the config needs to get flattened so that deeply nested keys get new keys that
        are a sum of their parents' keys.

        See the corresponding test cases for examples.

        Not the most pleasant thing to work with from an end user perspective, but it beats out
        having to just remove the deeply nested sections all together.
        """
        flattened_config = {}  # type: Dict[str, Any]

        for key, value in self.config.items():
            if isinstance(value, dict):
                flattened_config[key] = self._flatten_config_recursive(value, "")
            elif isinstance(value, list):
                # Check if the list is all primitive types (i.e. not dicts or lists)
                # Otherwise, lists of dicts or lists of lists must be flattened to a dict
                if not all(isinstance(item, dict) or isinstance(item, list) for item in value):
                    flattened_config[key] = value
                else:
                    flattened_config[key] = self._flatten_config_recursive(value, "")
            else:
                flattened_config[key] = value

        return flattened_config

    def update_config(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._write_config()

    def get_value(self, key_path: str) -> Any:
        try:
            value = reduce(operator.getitem, key_path.split("."), self.config)
        except Exception as e:
            logger.debug(traceback.format_exc())
            value = None

        return value

    def set_value(self, key_path: str, value: Any) -> None:
        if isinstance(value, str):
            try:
                value_json = json.loads(value)
            except ValueError:
                # The value wasn't valid json; this can happen with values that aren't
                # formatted as literal strings (i.e. with quotes).
                # Here, we convert the value to a valid json string (i.e. by quoting it)
                # and then converting it back to a json 'object'.
                value_json = json.loads(json.dumps(value))
        else:
            value_json = value

        try:
            temp_config = self.config
            keys = key_path.split(".")

            for index, key in enumerate(keys):
                temp_config.setdefault(key, {})

                if index == (len(keys) - 1):
                    temp_config[key] = value_json
                else:
                    temp_config = temp_config[key]

            self._write_config()
        except Exception as e:
            logger.exception(e)  # type: ignore
            raise click.Abort()

    def get_project_path(self, sub_path: str) -> str:
        return os.path.join(self.config_dir, sub_path)

    def _search_for_file_dir(self, file_name: str) -> str:
        current_dir = os.getcwd()

        # Search the current and all parent directories for the file
        file_list = os.listdir(current_dir)
        parent_dir = os.path.dirname(current_dir)

        while file_name not in file_list and current_dir != parent_dir:
            current_dir = parent_dir

            file_list = os.listdir(current_dir)
            parent_dir = os.path.dirname(current_dir)

        if current_dir == parent_dir:
            logger.error(
                "Could not find '{}' in the current or parent directories. "
                "Is this a Kubails project?".format(file_name)
            )

            raise click.Abort()
        else:
            return current_dir

    def _open_config(self) -> Dict[str, Any]:
        file_name = self.config_path

        try:
            with open(file_name, "r") as f:
                config = json.load(f)

            logger.debug("Parsed {}: {}".format(file_name, config))
            return config
        except IOError:
            logger.error("Error while reading {}. Is this a Kubails project?".format(file_name))
            raise click.Abort()

    def _write_config(self) -> None:
        file_name = self.config_path

        try:
            with open(file_name, "w") as f:
                json.dump(self.config, f, indent=4, sort_keys=True)

            logger.debug("Wrote {} to {}".format(self.config, file_name))
        except IOError as e:
            logger.error("Error while reading {}. Is this a Kubails project?".format(file_name))
            raise click.Abort()

    def _parse_config(self, config: Dict[str, Any]) -> None:
        self.apis_to_enable = [
            "cloudkms.googleapis.com",
            "cloudbuild.googleapis.com",
            "cloudfunctions.googleapis.com",
            "cloudresourcemanager.googleapis.com",
            "compute.googleapis.com",
            "container.googleapis.com",
            "containerregistry.googleapis.com",
            "dns.googleapis.com",
            "iam.googleapis.com",
            "replicapool.googleapis.com",
            "replicapoolupdater.googleapis.com",
            "resourceviews.googleapis.com",
            "secretmanager.googleapis.com",
            "sourcerepo.googleapis.com"
        ]

        self.container_admin_role = "roles/container.admin"
        self.service_account_token_creator_role = "roles/iam.serviceAccountTokenCreator"
        self.service_account_key_admin_role = "roles/iam.serviceAccountKeyAdmin"
        self.crypto_key_decrypter_role = "roles/cloudkms.cryptoKeyDecrypter"
        self.secret_manager_role = "roles/secretmanager.admin"

        self.values_folder = "helm/values"

        self.gcp_project_id = config.get("__gcp_project_id")
        self.gcp_project_region = config.get("__gcp_project_region")
        self.gcp_project_zone = config.get("__gcp_project_zone")

        self.project_title = config.get("__project_title")
        self.project_name = config.get("__project_name")

        self.service_account = "{}-account".format(self.project_name)
        self.service_account_role = "roles/editor"
        self.repo_admin_role = "roles/source.admin"
        self.logs_configuration_writer_role = "roles/logging.configWriter"
        self.project_iam_admin_role = "roles/resourcemanager.projectIamAdmin"

        self.services = config.get("__services", {})  # type: Dict[str, Dict[str, Any]]
        self.services_with_code = self._parse_services_with_code(self.services)
        self.services_with_secrets = self._parse_services_with_secrets(self.services)

        self.domain = config.get("__domain")

        self.production_namespace = config.get("__production_namespace")

        self.terraform_state_bucket = config.get("__terraform_bucket", "{}-terraform".format(self.project_name))

    def _flatten_config_recursive(self, config: Union[Dict[str, Any], List[Any]], parent_key: str) -> Dict[str, Any]:
        flattened_config = {}
        key_prefix = parent_key + "__" if parent_key else ""
        iterable = enumerate(config) if isinstance(config, list) else config.items()

        # The reason to ignore the type is that mypy can't pick up that iterable is going
        # to be iterable; it just thinks it's an object
        for key, value in iterable:  # type: ignore
            if isinstance(value, dict) or isinstance(value, list):
                sub_config = self._flatten_config_recursive(value, str(key))
                flattened_config.update({key_prefix + k: v for k, v in sub_config.items()})
            else:
                flattened_config[key_prefix + str(key)] = value

        return flattened_config

    def _parse_services_with_code(self, services: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(services, dict):
            return {k: v for k, v in services.items() if "folder" not in v or v.get("folder")}
        else:
            return None

    def _parse_services_with_secrets(self, services: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(services, dict):
            return {k: v for k, v in services.items() if "secrets" in v and v.get("secrets")}
        else:
            return None
