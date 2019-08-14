import json
import logging
import os
import shutil
from functools import reduce
from typing import List
from kubails.utils.service_helpers import call_command, get_command_output, get_codebase_folder, get_codebase_subfolder


logger = logging.getLogger(__name__)

BUILDER_IMAGE = "kubails-builder"


class GoogleCloud:
    def __init__(self, project_id, project_region, project_zone):
        self.project_id = project_id
        self.project_region = project_region
        self.project_zone = project_zone

        self.base_command = ["gcloud", "--project", self.project_id]

    def set_project(self) -> bool:
        logger.info("Switching to project {}...".format(self.project_id))

        command = ["gcloud", "config", "set", "project", self.project_id]
        return call_command(command)

    def deploy_builder_image(self) -> bool:
        logger.info("Deploying the Kubails Builder image...")

        root_folder = get_codebase_folder()
        root_kubails_folder = os.path.join(root_folder, "kubails")
        builder_folder = get_codebase_subfolder("builder")
        builder_kubails_folder = os.path.join(builder_folder, "kubails")
        cloudbuild_config = os.path.join(builder_folder, "cloudbuild.yaml")

        if os.path.exists(builder_kubails_folder):
            shutil.rmtree(builder_kubails_folder)

        shutil.copytree(root_folder, root_kubails_folder)
        shutil.move(os.path.join(root_folder, "kubails"), builder_folder)

        command = self.base_command + ["builds", "submit", builder_folder, "--config={}".format(cloudbuild_config), "--timeout=20m"]
        result = False

        try:
            result = call_command(command)
        finally:
            shutil.rmtree(builder_kubails_folder)

        return result

    def delete_builder_image(self) -> bool:
        logger.info("Destroying the Kubails Builder image...")

        command = self.base_command + [
            "container", "images", "delete", "-q",
            "gcr.io/{}/{}:latest".format(self.project_id, BUILDER_IMAGE),
            "--force-delete-tags"
        ]

        return call_command(command)

    def create_service_account(self, service_account: str, project_title: str) -> bool:
        logger.info("Creating service account {}...".format(service_account))

        command = self.base_command + [
            "iam", "service-accounts",
            "create", service_account,
            "--display-name", "{} service account".format(project_title)
        ]

        return call_command(command)

    def delete_service_account(self, service_account: str) -> bool:
        logger.info("Deleting service account {}...".format(service_account))

        full_service_account = self._format_full_service_account(service_account)
        command = self.base_command + ["iam", "service-accounts", "delete", "-q", full_service_account]
        return call_command(command)

    def create_key_for_service_account(self, service_account: str, key_folder: str = ".") -> bool:
        logger.info("Creating key for service account {}...".format(service_account))

        key_file = self._format_service_account_key(service_account, key_folder)

        if os.path.isfile(key_file):
            logger.info("Key for service account {} already exists.".format(service_account))
            return True

        full_service_account = self._format_full_service_account(service_account)

        command = self.base_command + [
            "iam", "service-accounts", "keys",
            "create", key_file,
            "--iam-account", full_service_account
        ]

        key_created = call_command(command)

        # Remove the json file when the command fails.
        # This is because gcloud will still create a json file even
        # if the service account doesn't exist (or the user is missing permissions)
        if not key_created:
            os.remove(key_file)

        return key_created

    def delete_key_for_service_account(self, service_account: str, key_folder: str = ".") -> bool:
        key_file = self._format_service_account_key(service_account, key_folder)

        if not os.path.isfile(key_file):
            logger.info("Key for service account {} doesn't exist.".format(service_account))
            return True

        try:
            with open(key_file, "r") as f:
                key_file_json = json.load(f)

            key_id = key_file_json["private_key_id"]
        except KeyError as e:
            logger.error("Invalid key file {}. Missing 'private_key_id' field.".format(key_file))
            return False

        full_service_account = self._format_full_service_account(service_account)

        command = self.base_command + [
            "iam", "service-accounts", "keys",
            "delete", key_id,
            "--iam-account", full_service_account,
            "--quiet"
        ]

        os.remove(key_file)
        return call_command(command)

    def enable_apis(self, apis_to_enable: List[str]) -> bool:
        logger.info("Enabling APIs...")

        commands = list(map(lambda api: self.base_command + ["services", "enable", api], apis_to_enable))
        return reduce(lambda acc, command: call_command(command) and acc, commands)

    def create_bucket(self, bucket_name: str) -> bool:
        logger.info("Creating bucket {}...".format(bucket_name))

        command = ["gsutil", "mb", "gs://{}".format(bucket_name)]
        return call_command(command)

    def delete_bucket(self, bucket_name: str) -> bool:
        logger.info("Deleting bucket {}...".format(bucket_name))

        command = ["gsutil", "rm", "-r", "gs://{}".format(bucket_name)]
        return call_command(command)

    def add_role_to_service_account(self, service_account: str, role: str) -> bool:
        logger.info("Binding service account {} to role {}...".format(service_account, role))

        full_service_account = self._format_full_service_account(service_account)
        return self.add_role_to_entity("serviceAccount", full_service_account, role)

    def add_role_to_current_user(self, role) -> bool:
        user = self.get_current_user_email()
        logger.info("Binding user {} to role {}...".format(user, role))

        return self.add_role_to_entity("user", user, role)

    def delete_role_from_service_account(self, service_account: str, role: str) -> bool:
        logger.info("Removing role binding {} on service account {}...".format(role, service_account))

        full_service_account = self._format_full_service_account(service_account)
        return self.delete_role_from_entity("serviceAccount", full_service_account, role)

    def add_role_to_entity(self, entity_type: str, entity: str, role: str) -> bool:
        command = self.base_command + [
            "projects", "add-iam-policy-binding", self.project_id,
            "--member", "{}:{}".format(entity_type, entity),
            "--role", role
        ]

        return call_command(command)

    def delete_role_from_entity(self, entity_type: str, entity: str, role: str) -> bool:
        command = self.base_command + [
            "projects", "remove-iam-policy-binding", self.project_id, "-q",
            "--member", "{}:{}".format(entity_type, entity),
            "--role", role
        ]

        return call_command(command)

    def authenticate_cluster(self, cluster: str) -> bool:
        command = self.base_command + [
            "container", "clusters", "get-credentials",
            "--zone", self.project_zone, cluster
        ]

        return call_command(command)

    def kms_encrypt(self, input_file, encrypted_file: str, keyring: str, key: str) -> bool:
        command = self.base_command + [
            "kms", "encrypt",
            "--ciphertext-file", encrypted_file,
            "--plaintext-file", input_file,
            "--location", self.project_region,
            "--keyring", keyring,
            "--key", key
        ]

        return call_command(command, shell=True)

    def kms_decrypt(self, encrypted_file: str, decrypted_file: str, keyring: str, key: str) -> bool:
        command = self.base_command + [
            "kms", "decrypt",
            "--ciphertext-file", encrypted_file,
            "--plaintext-file", decrypted_file,
            "--location", self.project_region,
            "--keyring", keyring,
            "--key", key
        ]

        return call_command(command, shell=True)

    def get_current_user_email(self) -> str:
        command = self.base_command + ["config", "get-value", "account"]
        return get_command_output(command)

    def get_project_number(self) -> str:
        command = self.base_command + ["projects", "describe", self.project_id, "--format='value(projectNumber)'"]
        return get_command_output(command, shell=True)

    def get_cloud_build_service_account(self) -> str:
        project_number = self.get_project_number()
        return "{}@cloudbuild.gserviceaccount.com".format(project_number)

    def _format_full_service_account(self, service_account: str) -> str:
        return "{}@{}.iam.gserviceaccount.com".format(service_account, self.project_id)

    def _format_service_account_key(self, service_account: str, key_folder: str) -> str:
        return os.path.join(key_folder, "{}.json".format(service_account))
