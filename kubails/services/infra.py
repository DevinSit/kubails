import logging
import sys
from typing import List
from kubails.external_services import dependency_checker, gcloud, terraform
from kubails.services import config_store, cluster


logger = logging.getLogger(__name__)


@dependency_checker.check_dependencies()
class Infra:
    def __init__(self):
        self.config = config_store.ConfigStore()

        self.gcloud = gcloud.GoogleCloud(
            self.config.gcp_project_id,
            self.config.gcp_project_region,
            self.config.gcp_project_zone
        )

        self.terraform = terraform.Terraform(self.config.get_flattened_config(), root_folder=self.config.config_dir)

        self.cluster = cluster.Cluster()

    def setup(self) -> None:
        # Enable the APIs first before anything else so that subsequent commands can use those resources.
        self.gcloud.enable_apis(self.config.apis_to_enable)

        self.gcloud.deploy_builder_image()

        # Create the service account that will be used for Terraform and whatnot.
        self.gcloud.create_service_account(self.config.service_account, self.config.project_title)

        self.gcloud.add_role_to_service_account(self.config.service_account, self.config.service_account_role)
        self.gcloud.add_role_to_service_account(self.config.service_account, self.config.repo_admin_role)
        self.gcloud.add_role_to_service_account(self.config.service_account, self.config.logs_configuration_writer_role)
        self.gcloud.add_role_to_service_account(self.config.service_account, self.config.project_iam_admin_role)

        self.gcloud.create_key_for_service_account(self.config.service_account)

        # Enable the Cloud Build service account to be able to administer GKE and generate service account keys.
        cloud_build_service_account = self.gcloud.get_cloud_build_service_account()

        self.gcloud.add_role_to_entity(
            "serviceAccount", cloud_build_service_account, self.config.container_admin_role
        )

        self.gcloud.add_role_to_entity(
            "serviceAccount", cloud_build_service_account, self.config.service_account_key_admin_role
        )

        self.gcloud.add_role_to_entity(
            "serviceAccount", cloud_build_service_account, self.config.crypto_key_decrypter_role
        )

        # Create the Terraform state bucket (if it doesn't already exist) and initialize Terraform to use it.
        terraform_bucket = self.config.terraform_state_bucket

        if self.gcloud.does_bucket_exist_in_another_project(terraform_bucket):
            print()
            logger.info(
                "Sorry, bucket '{}' already exists in another project. "
                "Please add/change the '__terraform_bucket' value in 'kubails.json' "
                "to a different bucket name.".format(terraform_bucket)
            )

            sys.exit(1)
        elif not self.gcloud.does_bucket_exist_in_project(terraform_bucket):
            self.gcloud.create_bucket(terraform_bucket)
        else:
            print()
            logger.info("Terraform bucket '{}' already exists in project.".format(terraform_bucket))

        self.terraform.init()

    def cleanup(self) -> None:
        self.gcloud.delete_builder_image()

        self.gcloud.delete_role_from_service_account(self.config.service_account, self.config.service_account_role)
        self.gcloud.delete_service_account(self.config.service_account)

        self.gcloud.delete_bucket(self.config.terraform_state_bucket)

    def authenticate(self) -> bool:
        result = self.gcloud.create_key_for_service_account(
            self.config.service_account,
            key_folder=self.config.config_dir
        )

        if result:
            result = result and self.terraform.init()

        return result

    def unauthenticate(self) -> bool:
        return self.gcloud.delete_key_for_service_account(
            self.config.service_account,
            key_folder=self.config.config_dir
        )

    def deploy(self) -> bool:
        result = self.terraform.deploy()

        if result:
            self.cluster.update_manifests_from_terraform()

        return result

    def deploy_builder(self):
        self.gcloud.deploy_builder_image()

    def destroy(self) -> None:
        self.cluster.destroy_ingress()
        self.terraform.destroy()

    def terraform_command(self, command: str, arguments: List[str], with_vars=False) -> None:
        self.terraform.run_command(command, arguments, with_vars=with_vars)

    def get_name_servers(self) -> str:
        return self.terraform.get_name_servers()
