import click
import logging
import sys
from typing import Tuple
from kubails.commands import helpers
from kubails.services.service import Service
from kubails.templates import SERVICE_TEMPLATES
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Service '{}' args")

service_service = None


@click.group()
def service():
    """Manage the services for your project."""
    global service_service

    service_service = Service()


@service.command()
@click.argument("service", nargs=-1)
@log_command_args
def start(service: Tuple[str]) -> None:
    """Start up your services locally."""
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
    """Lint your services."""
    if not service_service.lint(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("service", nargs=-1)
@click.option("--tag")
@log_command_args
def test(service: Tuple[str], tag) -> None:
    """Test your services."""
    if not service_service.test(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("service", nargs=-1)
@click.option("--tag")
@log_command_args
def ci(service: Tuple[str], tag: str) -> None:
    """Run CI on your services."""
    if not service_service.ci(list(service), tag):
        sys.exit(1)


@service.command()
@click.argument("command", required=True)
@log_command_args
def make(command: str) -> None:
    """Execute a Make command on your services."""
    if not service_service.make(command):
        sys.exit(1)


@service.command()
@click.option(
    "--type", "service_type",
    prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["service_type"],
    type=click.Choice(SERVICE_TEMPLATES),
    default=SERVICE_TEMPLATES[0]
)
@click.option(
    "--subdomain",
    prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["subdomain"],
    default=""
)
@click.option("--title", prompt=helpers.SERVICE_GENERATION_PROMPTS["without_index"]["title"])
@log_command_args
def generate(service_type: str, subdomain: str, title: str) -> None:
    """Generate a new service."""
    helpers.generate_service(
        service_service,
        service_type=service_type,
        subdomain=subdomain,
        title=title,
    )


############################################################
# Images sub-group
############################################################


@service.group()
def images():
    """Build and push Docker images for your services."""
    pass


@images.command()
@click.argument("service", nargs=-1)
@click.option("--branch")
@click.option("--commit")
@log_command_args
def build(service: Tuple[str], branch: str, commit: str) -> None:
    """Build the Docker image for a service."""
    if not service_service.build(list(service), branch, commit):
        sys.exit(1)


@images.command()
@click.argument("service", nargs=-1)
@click.option("--branch")
@click.option("--commit")
@log_command_args
def push(service: Tuple[str], branch: str, commit: str) -> None:
    """Push the Docker image for a service."""
    if not service_service.push(list(service), branch, commit):
        sys.exit(1)
