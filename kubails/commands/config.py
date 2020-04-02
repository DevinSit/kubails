import click
import json
import logging
from kubails.services.config_store import ConfigStore
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Config '{}' args")

config_service = None


@click.group()
def config():
    """Manage your Kubails configuration."""
    global config_service

    config_service = ConfigStore()


@config.command()
@click.option("--flattened", default=False, is_flag=True)
@log_command_args
def list(flattened: bool) -> None:
    """Display your Kubails configuration as json."""
    config = config_service.get_flattened_config() if flattened else config_service.get_config()
    logger.info(json.dumps(config, indent=4, sort_keys=True))


@config.command()
@click.argument("key_path")
@log_command_args
def get(key_path: str) -> None:
    """Get a value from your Kubails configuration."""
    value = config_service.get_value(key_path)
    logger.info(json.dumps(value, indent=4, sort_keys=True))


@config.command()
@click.argument("key_path")
@click.argument("value")
def set(key_path: str, value: str) -> None:
    """Set a value for your Kubails configuration."""
    config_service.set_value(key_path, value)
