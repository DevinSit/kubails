import click
import logging
import os
from dotenv import dotenv_values
from typing import List
from kubails.external_services import gcloud, helm, kubectl, terraform
from kubails.services import config_store, manifest_manager
from kubails.utils.service_helpers import call_command, sanitize_name


logger = logging.getLogger(__name__)


class Cluster:
    def __init__(self):
        self.config = config_store.ConfigStore()

        self.gcloud = gcloud.GoogleCloud(
            self.config.gcp_project_id,
            self.config.gcp_project_region,
            self.config.gcp_project_zone
        )

        self.helm = helm.Helm(self.config.get_project_path("helm"), self.config.config_path)
        self.kubectl = kubectl.Kubectl()
        self.terraform = terraform.Terraform(self.config.get_flattened_config(), root_folder=self.config.config_dir)

        self.manifest_manager = manifest_manager.ManifestManager(
            manifests_folder=self.config.get_project_path("manifests")
        )

    def authenticate(self) -> None:
        cluster_name = self.terraform.get_cluster_name()
        self.gcloud.authenticate_cluster(cluster_name)

    def deploy(self) -> None:
        self.authenticate()

        self.deploy_storage_classes()
        self.deploy_ingress_controller()
        self.deploy_cert_manager()
        self.deploy_certificate_reflector()

    def destroy(self) -> None:
        self.destroy_ingress()
        self.terraform.destroy_cluster()

    def destroy_ingress(self) -> None:
        # Need to delete the ingress so that GKE properly deletes the load balancer resource.
        # Otherwise, if only Terraform goes and deletes the cluster, the load balancer will stick around.
        if self.terraform.cluster_deployed():
            logger.info("Destroying ingress load balancer...")
            self.kubectl.delete_namespace("ingress-nginx")

    def deploy_storage_classes(self) -> None:
        storage_class_manifests = self.manifest_manager.static_manifest_location("storage-classes")
        self.kubectl.deploy(storage_class_manifests, recursive=True)

    def deploy_ingress_controller(self) -> None:
        ingress_manifests = self.manifest_manager.static_manifest_location("nginx-ingress-controller")
        user_email = self.gcloud.get_current_user_email()
        bind_name = "{}-cluster-admin-binding".format(user_email)

        self.kubectl.create_cluster_role_binding(bind_name, "cluster-admin", user_email)
        self.kubectl.deploy(ingress_manifests, recursive=True)

    def deploy_cert_manager(self) -> None:
        cert_manager_manifests = self.manifest_manager.static_manifest_location("cert-manager")
        self.kubectl.deploy(cert_manager_manifests, recursive=True)

        service_account_file = "service-account.json=./{}.json".format(self.config.service_account)
        self.kubectl.create_secret_from_file("clouddns-service-account", service_account_file, "cert-manager")

    def deploy_certificate_reflector(self) -> None:
        certificate_reflector_manifests = self.manifest_manager.static_manifest_location("certificate-reflector")
        self.kubectl.deploy(certificate_reflector_manifests)

    def update_manifests_from_terraform(self) -> None:
        ingress_manifest_location = "nginx-ingress-controller/2-cloud-generic.yaml"

        public_ip = self.terraform.get_public_ip()
        ingress_manifest = self.manifest_manager.load_static_manifest(ingress_manifest_location)

        ingress_manifest["spec"]["loadBalancerIP"] = public_ip
        self.manifest_manager.write_static_manifest(ingress_manifest, ingress_manifest_location)

    def generate_manifests(self, services: List[str], tag: str = "", namespace: str = "") -> bool:
        result = True
        namespace = sanitize_name(namespace)

        is_production = namespace == self.config.production_namespace
        subdomain = "" if is_production else "{}.".format(namespace)
        tag = tag if tag else "latest"

        result = result and self.cleanup_manifests()
        logger.info("Generating new manifests...")

        services_dict = {s: self.config.services[s] for s in services} if services else self.config.services

        for service, config in services_dict.items():
            output_dir = os.path.join(self.manifest_manager.generated_manifest_location(""), service)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            value_files = ["values.yaml"]
            template_files = list(map(lambda x: "{}.yaml".format(x), config.get("templates", [])))
            replicas = config.get("production_replicas", 0) if is_production else config.get("replicas", 0)

            string_vars = [
                "image={}".format(config["image"]),
                "tag={}".format(tag),
                "namespace={}".format(namespace),
                "subdomain={}".format(subdomain),
                "replicas={}".format(replicas),
                "serviceName={}".format(service)
            ]

            result = result and self.helm.template(
                output_dir,
                value_files=value_files,
                template_files=template_files,
                string_vars=string_vars
            )

        logger.info("Finished generating manifests.")
        return result

    def deploy_manifests(self, services: List[str], namespace: str = "") -> bool:
        result = True
        namespace = sanitize_name(namespace)

        services_dict = {s: self.config.services[s] for s in services} if services else self.config.services

        if namespace:
            self.kubectl.create_namespace(namespace, label="kube-git-syncer=\"true\"")

        for service, config in services_dict.items():
            service_manifests = self.manifest_manager.generated_manifest_location(service)
            result = result and self.kubectl.deploy(service_manifests, recursive=True)

        return result

    def cleanup_manifests(self) -> bool:
        result = call_command([
            "find", self.manifest_manager.generated_manifest_location(""),
            "-type", "f",
            "-name", "'*.yaml'",
            "-delete"
        ], shell=True)

        logger.info("Removed old manifests.")
        return result

    def deploy_secrets(self, services: List[str], namespace: str) -> bool:
        result = True
        namespace = sanitize_name(namespace)

        services_dict = {
            s: self.config.services_with_secrets[s] for s in services
        } if services else self.config.services_with_secrets

        for service, config in services_dict.items():
            secrets_config = config.get("secrets", {})
            folder = config.get("folder", service)
            secret_name = secrets_config["name"]

            secrets_file = self.config.get_project_path(os.path.join("services", folder, secrets_config["file"]))
            decrypted_secrets_file = "decrypted_secrets"

            result = result and self.gcloud.kms_decrypt(
                encrypted_file=secrets_file,
                decrypted_file=decrypted_secrets_file,
                keyring=self.terraform.get_kms_key_ring_name(),
                key=self.terraform.get_kms_key_name()
            )

            self.kubectl.delete_secret(secret_name, namespace)
            result = result and self.kubectl.create_secret_from_file(
                secret_name, decrypted_secrets_file, namespace, is_env_file=True
            )

            try:
                os.remove(decrypted_secrets_file)
            except OSError as e:
                logger.exception(e)  # type: ignore
                return False

            if not result:
                return result

        return result

    def create_secret(self, file_name: str, service: str, secret_name: str) -> None:
        encrypted_file = "{}.encrypted".format(os.path.basename(file_name))
        env_variables = dotenv_values(stream=file_name)

        if not env_variables:
            logger.error("{} is either empty or an invalid env file. Not encrypting.".format(file_name))
            raise click.Abort()

        self.gcloud.kms_encrypt(
            input_file=file_name,
            encrypted_file=encrypted_file,
            keyring=self.terraform.get_kms_key_ring_name(),
            key=self.terraform.get_kms_key_name()
        )

        secrets_config = {"name": secret_name, "file": encrypted_file, "variables": list(env_variables.keys())}
        self.config.set_value("__services.{}.secrets".format(service), secrets_config)

        logger.info("Created {} and updated kubails.json with secrets info.".format(encrypted_file))
