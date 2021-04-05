import logging
import os
from typing import Callable, Dict, List
from kubails.external_services import dependency_checker, docker, docker_compose, gcloud
from kubails.services import config_store, manifest_manager, templater
from kubails.resources.templates import ConfigGenerator, SERVICES_CONFIG
from kubails.utils.service_helpers import call_command, sanitize_name


logger = logging.getLogger(__name__)

SERVICES_FOLDER = config_store.SERVICES_FOLDER

DEFAULT_KUBAILS_SERVICE_CONFIG = {
    "container_port": "",
    "env": [],
    "external_port": "",
    "host": "",
    "folder": "",
    "image": "",
    "image_in_project": True,
    "persistent_volume": {},
    "pre_startup_command": None,
    "production_replicas": 1,
    "replicas": 1,
    "secrets": {},
    "templates": [],
    "type": "",
    "wait_for_service": None
}


@dependency_checker.check_dependencies()
class Service:
    def __init__(self):
        self.config = config_store.ConfigStore()

        self.docker = docker.Docker()

        self.docker_compose = docker_compose.DockerCompose(
            self.config.project_name,
            self.config.get_project_path("services")
        )

        self.gcloud = gcloud.GoogleCloud(
            self.config.gcp_project_id,
            self.config.gcp_project_region,
            self.config.gcp_project_zone
        )

        self.manifest_manager = manifest_manager.ManifestManager(
            manifests_folder=self.config.get_project_path("manifests")
        )

    def start(self, services: List[str]) -> None:
        print()
        logger.info("Starting services locally...")
        print()

        self.docker_compose.up(services)

    def destroy(self) -> None:
        print()
        logger.info("Destroying service containers, networks, and volumes...")
        print()

        self.docker_compose.down()

    def lint(self, services: List[str], tag: str) -> bool:
        return self._run_services_make_command("lint", services, tag)

    def test(self, services: List[str], tag: str) -> bool:
        return self._run_services_make_command("test", services, tag)

    def ci(self, services: List[str], tag: str) -> bool:
        return self._run_services_make_command("ci", services, tag)

    def make(self, command: str) -> bool:
        """Run a make command across all of the services."""
        return self._run_services_make_command(command)

    def build(self, services: List[str], branch_tag: str = None, commit_tag: str = None) -> bool:
        branch_tag = sanitize_name(branch_tag)

        def build_function(service: str) -> bool:
            service_path = self._get_service_path(service)
            fixed_tag = self._get_fixed_tag(service)
            base_images = self._get_base_images(service)

            stage_images = []  # type: List[str]
            result = True

            for index, base_image in enumerate(base_images):
                is_last_image = index == len(base_images) - 1
                tagged_images = self._generate_tagged_images(base_image, branch_tag, commit_tag, fixed_tag=fixed_tag)

                if not branch_tag and not commit_tag:  # Local dev use case
                    result = result and self.docker.build(service_path, [tagged_images["latest"]])
                else:  # CI/CD pipeline use case
                    cache_image = tagged_images["fixed_tag"] if fixed_tag else tagged_images["branch"]
                    master_cache_image = tagged_images["master"]

                    # Each previous stage image is used to build the next stage.
                    cache_images = stage_images + [cache_image, master_cache_image]
                    stage_images.append(cache_image)

                    # If we're on the last image, then that means it's the final stage and
                    # # we don't need to specify a target stage.
                    # Otherwise, each previous stage needs to specify a target in the Dockerfile to be
                    # built (and pushed) separately.
                    target_stage = None if is_last_image else base_image

                    result = result and self.docker.build(
                        service_path,
                        list(tagged_images.values()),
                        target_stage=target_stage,
                        cache_images=cache_images,
                        branch=branch_tag
                    )

            return result

        return self._apply_to_services(build_function, services)

    def push(self, services: List[str], branch_tag: str = None, commit_tag: str = None) -> bool:
        branch_tag = sanitize_name(branch_tag)

        def push_function(service: str) -> bool:
            fixed_tag = self._get_fixed_tag(service)
            base_images = self._get_base_images(service)

            result = True

            for base_image in base_images:
                tagged_images = self._generate_tagged_images(base_image, branch_tag, commit_tag, fixed_tag=fixed_tag)

                if not branch_tag and not commit_tag:  # Local dev use case
                    result = result and self.docker.push(tagged_images["latest"])
                else:  # CI/CD pipeline use case

                    if fixed_tag:
                        result = result and self.docker.push(tagged_images["fixed_tag"])
                    else:
                        result = result and self.docker.push(tagged_images["branch"])
                        result = result and self.docker.push(tagged_images["commit"])

                        if branch_tag == self.config.production_namespace:
                            result = result and self.docker.push(tagged_images["latest"])

            return result

        return self._apply_to_services(push_function, services)

    def generate(
        self,
        service_type: str,
        title: str,
        name: str,
        subdomain: str,
        extra_config: Dict[str, str]
    ) -> None:
        name = name.lower().replace(" ", "-")
        subdomain = subdomain.lower().replace(" ", "-")
        config_generator = SERVICES_CONFIG[service_type](name, self.config, extra_config)

        print()  # Just a new line for user output

        self._template_service(service_type, title, name)
        self._add_service_to_kubails_config(config_generator, name, subdomain)
        self._add_service_to_compose_config(config_generator, name)

        if config_generator.is_external_service():
            self._update_wildcard_certificate()

    def _run_services_make_command(self, command: str, services: List[str] = [], tag: str = "") -> bool:
        tag = sanitize_name(tag)

        def function(service: str) -> bool:
            base_image = self._get_base_images(service)[-1]

            cache_image = self.gcloud.format_gcr_image(self.config.project_name, base_image, tag)
            cache_option = "" if not tag else "--cache-from={}".format(cache_image)

            full_command = [
                "make", "-C", self._get_service_path(service), command, "CACHE={}".format(cache_option)
            ]

            return call_command(full_command, shell=True)

        return self._apply_to_services(function, services)

    def _apply_to_services(self, function: Callable[[str], bool], services: List[str] = []) -> bool:
        """
        Takes a function and 'applies' it to each of the services (either the given services or
        all of the services that have code). i.e. it just runs the function with each service.

        It is important that this (and functions that use this) can exit with False,
        so that the CLI layer can catch it and exit with an error code.
        Otherwise, the CI pipeline won't know when a step has failed.
        """

        services_iterable = services if services else self.config.services_with_code

        for service in services_iterable:  # type: ignore
            if not function(service):
                return False  # Fail fast to optimize the CI/CD pipeline

        return True

    def _get_service_path(self, service: str) -> str:
        folder = self.config.get_service_folder(service)
        return self.config.get_project_path(os.path.join(SERVICES_FOLDER, folder))

    def _get_base_images(self, service: str) -> List[str]:
        base_image = self.config.services.get(service, {}).get("image", service)
        image_stages = self.config.services.get(service, {}).get("image_stages", [])

        # If `image_stages` is provided in the config, then that means that the service uses a multi-stage Dockerfile.
        # As such, we want to build the specified stages before the final image, so that we can push them separately,
        # so that we can cache them separately, so that we actually cache improvements for subsequent builds.
        #
        # If we don't cache each stage image separately, then we get no caching for the final image, since it
        # will be completely separate from the previous stages.
        #
        # Note: The values listed in `image_stages` must correspond to the names of the stages in the Dockerfile
        # If a stage is declared as `FROM node:14 as build-env`, then `image_stages` must contain `build-env`.
        # This is because the images are tagged the same as the stages.
        return image_stages + [base_image]

    def _get_fixed_tag(self, service: str) -> str:
        return self.config.services.get(service, {}).get("fixed_tag", None)

    def _generate_tagged_images(
        self,
        base_image: str,
        branch_tag: str = "",
        commit_tag: str = "",
        fixed_tag: str = None
    ) -> Dict[str, str]:
        images = {}

        images["base"] = self.gcloud.format_gcr_image(self.config.project_name, base_image)

        images["latest"] = "{}:latest".format(images["base"])
        images["master"] = "{}:master".format(images["base"])
        images["branch"] = "{}:{}".format(images["base"], branch_tag)
        images["commit"] = "{}:{}".format(images["base"], commit_tag)
        images["fixed_tag"] = "{}:{}".format(images["base"], fixed_tag)

        return images

    def _template_service(self, service_type: str, title: str, name: str) -> None:
        output_dir = self.config.get_project_path(SERVICES_FOLDER)
        templater.Templater.template_service(service_type, title, name, output_dir)

        logger.info("Created {}".format(os.path.join(SERVICES_FOLDER, name)))

    def _add_service_to_kubails_config(self, config_generator: ConfigGenerator, name: str, subdomain: str) -> None:
        generated_service_config = config_generator.generate_kubails_config()

        # Setup the basic service config
        service_config = {name: DEFAULT_KUBAILS_SERVICE_CONFIG.copy()}
        service_config[name]["folder"] = name
        service_config[name]["image"] = name

        host = "{}.{}".format(subdomain, self.config.domain) if subdomain else self.config.domain
        service_config[name]["host"] = host

        # Merge in the service-specific generated config
        service_config[name].update(generated_service_config[name])

        # Add in any other services that might be included with the primary
        for key, value in generated_service_config.items():
            if key != name:
                service_config[key] = DEFAULT_KUBAILS_SERVICE_CONFIG.copy()
                service_config[key].update(value)

        config = self.config.get_config()
        config["__services"].update(service_config)
        self.config.update_config(config)

        logger.info("Updated kubails.json with new service config")

    def _add_service_to_compose_config(self, config_generator: ConfigGenerator, name: str) -> None:
        if config_generator.has_compose_database_volume():
            data_volume = "{}-database-data".format(name)
            self.docker_compose.add_volume_config({data_volume: {"driver": "local"}})

        if config_generator.has_compose_deps_volume():
            deps_volume = "{}-deps".format(name)
            self.docker_compose.add_volume_config({deps_volume: None})

        generated_compose_config = config_generator.generate_compose_config()

        if generated_compose_config is not None:
            self.docker_compose.add_service_config(generated_compose_config)

            logger.info(
                "Updated {} with new service config".format(os.path.join(SERVICES_FOLDER, "docker-compose.yaml"))
            )

    def _update_wildcard_certificate(self) -> None:
        config = self.config.get_config()
        domains = [self.config.domain, "*.{}".format(self.config.domain)]

        for service, config in config["__services"].items():
            host = config.get("host", None)

            if "ingress" in config["templates"] and host is not None and host not in domains:
                domains.append("*.{}".format(host))

        certificate_manifest_location = "cert-manager/wildcard-certificate.yaml"
        certificate_manifest = self.manifest_manager.load_static_manifest(certificate_manifest_location)

        certificate_manifest["spec"]["dnsNames"] = domains
        self.manifest_manager.write_static_manifest(certificate_manifest, certificate_manifest_location)

        logger.info(
            "Updated {}; if the certificate has already been deployed, you should now update it "
            "by deleting the old secret and re-deploying the updated certificate".format(
                os.path.join(self.manifest_manager.static_folder, certificate_manifest_location)
            )
        )
