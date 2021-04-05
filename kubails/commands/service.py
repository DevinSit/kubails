import click
import logging
import sys
from typing import Tuple
from kubails.commands import helpers
from kubails.services.config_store import ConfigStore
from kubails.services.service import Service
from kubails.resources.templates import SERVICE_TEMPLATES
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Service '{}' args")

config_store = None
service_service = None


@click.group()
def service():
    """Manage the services for your project."""
    global config_store
    global service_service

    config_store = ConfigStore()
    service_service = Service()


@service.command()
@click.argument("service", nargs=-1)
@log_command_args
def start(service: Tuple[str]) -> None:
    """
    Start up SERVICE locally.

    If SERVICE is not specified, start all services.
    """
    service_service.start(list(service))


@service.command()
@log_command_args
def destroy() -> None:
    """Teardown your local services."""
    service_service.destroy()


@service.command()
@click.argument("service", nargs=-1)
@click.option("--tag")
@log_command_args
def lint(service: Tuple[str], tag: str) -> None:
    """
    Lint SERVICE.

    If SERVICE is not specified, lint all services.
    """
    if not service_service.lint(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("service", nargs=-1)
@click.option("--tag")
@log_command_args
def test(service: Tuple[str], tag) -> None:
    """
    Test SERVICE.

    If SERVICE is not specified, test all services.
    """
    if not service_service.test(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("service", nargs=-1)
@click.option("--tag")
@log_command_args
def ci(service: Tuple[str], tag: str) -> None:
    """
    Run CI on SERVICE.

    If SERVICE is not specified, run CI on all services.
    """
    if not service_service.ci(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("command", required=True)
@log_command_args
def make(command: str) -> None:
    """Execute a Make COMMAND on all your services."""
    if not service_service.make(command):
        sys.exit(1)


@service.command()
@click.option(
    "--type", "service_type",
    prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["service_type"],
    type=click.Choice(SERVICE_TEMPLATES),
    default=SERVICE_TEMPLATES[0],
    help="The template to base the service off of."
)
@click.option(
    "--subdomain",
    prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["subdomain"],
    default="",
    help="The subdomain the service will have when deployed."
)
@click.option(
    "--title",
    prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["title"],
    help="The title of the service."
)
@log_command_args
def generate(service_type: str, subdomain: str, title: str) -> None:
    """Generate a new service."""
    helpers.generate_service(
        service_service,
        service_type=service_type,
        subdomain=subdomain,
        title=title,
    )


@service.command()
@click.argument("service")
@log_command_args
def has_changed(service: str) -> None:
    """Returns whether or not the given service has changed since the last build."""
    if not config_store.is_changed_service(service):
        sys.exit(1)


############################################################
# Images sub-group
############################################################


@service.group()
def images():
    """Build and push Docker images for your services."""
    pass


@images.command()
@click.argument("service", nargs=-1)
@click.option("--branch", help="The branch to tag the image with.")
@click.option("--commit", help="The commit to tag the image with.")
@log_command_args
def build(service: Tuple[str], branch: str, commit: str) -> None:
    """
    Build the Docker image for SERVICE.

    If SERVICE is not specified, build all services' Docker images.
    """
    if not service_service.build(list(service), branch, commit):
        sys.exit(1)


@images.command()
@click.argument("service", nargs=-1)
@click.option("--branch", help="The branch the image was tagged with.")
@click.option("--commit", help="The commit the image was tagged with.")
@log_command_args
def push(service: Tuple[str], branch: str, commit: str) -> None:
    """
    Push the Docker image for SERVICE.

    If SERVICE is not specified, push all services' Docker images.
    """
    if not service_service.push(list(service), branch, commit):
        sys.exit(1)
