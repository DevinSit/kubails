import click
import logging
import os
import yaml
from typing import Any, Dict, List
from kubails.utils.service_helpers import call_command


logger = logging.getLogger(__name__)

COMPOSE_FILE = "docker-compose.yaml"


# We don't want 'null' to show up for 'None' when creating volumes, so blank them out.
def yaml_represent_none(self, data):
    return self.represent_scalar("tag:yaml.org,2002:null", "")


yaml.add_representer(type(None), yaml_represent_none)


class DockerCompose:
    def __init__(self, project_name: str, compose_folder: str) -> None:
        self.compose_file_location = os.path.join(compose_folder, COMPOSE_FILE)
        self.base_command = ["docker-compose", "-p", project_name, "--file", self.compose_file_location]

    def up(self, services: List[str]) -> bool:
        command = self.base_command + ["up", "--build"] + services
        return call_command(command)

    def down(self) -> bool:
        command = self.base_command + ["down", "-v"]
        return call_command(command)

    def add_service_config(self, new_service_config: Dict[str, Any]) -> None:
        config = self._read_config()
        config.setdefault("services", {})

        if not config["services"]:
            config["services"] = {}

        config["services"].update(new_service_config)

        self._write_config(config)

    def add_volume_config(self, new_volume: Dict[str, Any]) -> None:
        config = self._read_config()
        config.setdefault("volumes", {})

        if not config["volumes"]:
            config["volumes"] = {}

        config["volumes"].update(new_volume)

        self._write_config(config)

    def _read_config(self) -> Dict[str, Any]:
        with open(self.compose_file_location, "r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.exception("Failed to load docker-compose config: " + str(e))
                raise click.Abort()

    def _write_config(self, config: Dict[str, Any]) -> None:
        with open(self.compose_file_location, "w") as f:
            try:
                yaml.dump(config, f, default_flow_style=False, explicit_start=False, indent=4)
            except yaml.YAMLError as e:
                logger.exception("Failed to write docker-compose config: " + str(e))
                raise click.Abort()
