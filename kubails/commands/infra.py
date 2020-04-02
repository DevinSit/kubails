import click
import logging
import sys
from typing import Tuple
from kubails.services.infra import Infra
from kubails.services.cluster import Cluster
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Infra '{}' args")

infra_service = None
cluster_service = None


@click.group()
def infra():
    """Manage the infrastructure for your project."""
    global infra_service
    global cluster_service

    infra_service = Infra()
    cluster_service = Cluster()


@infra.command()
@log_command_args
def setup() -> None:
    """Configure your GCP project to work with Kubails."""
    infra_service.setup()


@infra.command()
@click.confirmation_option(
    prompt="This will delete the project's service account and destroy all Terraform state. Are you sure?"
)
@log_command_args
def cleanup() -> None:
    """Cleanup the resources created by 'setup'."""
    infra_service.cleanup()


@infra.command()
@log_command_args
def authenticate() -> None:
    """Generate a new Kubails service account key and initialize Terraform."""
    if not infra_service.authenticate():
        sys.exit(1)


@infra.command()
@log_command_args
def unauthenticate() -> None:
    """Removes your current key from the Kubails service account."""
    if not infra_service.unauthenticate():
        sys.exit(1)


@infra.command()
@click.option("--component", type=click.Choice(["all", "builder"]), default="all")
@log_command_args
def deploy(component: str) -> None:
    """Deploy the infrastructure needed for your Kubails project."""
    if component == "all":
        deploy_result = infra_service.deploy()

        if not deploy_result:
            sys.exit(1)

        name_servers = infra_service.get_name_servers()

        print()
        logger.info(
            "You should now point the name servers of your domain "
            "to the following before continuing:\n\n{}".format(name_servers)
        )
        print()

        if click.confirm("Have you changed the name servers?"):
            print()
            logger.info("Continuing with cluster deployment...")
            print()

            cluster_service.deploy()

            print()
            logger.info("Infrastructure deployment completed!")
            print()
    elif component == "builder":
        infra_service.deploy_builder()
    else:
        logger.error("WTF, how did you even trigger this?")


@infra.command()
@log_command_args
def destroy() -> None:
    """Destroy all of the infrastructure for your Kubails project."""
    message = (
        "This will delete all of the infrastructure for project '{}'. Are you sure?"
    ).format(infra_service.config.project_name)

    if click.confirm(message):
        if click.confirm("Are you really sure? You want to destroy EVERYTHING?"):
            infra_service.destroy()


@infra.command()
@click.argument("command")
@click.argument("arguments", nargs=-1)
@click.option("--with-vars", default=False, is_flag=True)
@log_command_args
def terraform(command: str, arguments: Tuple[str], with_vars: bool) -> None:
    """Run a Terraform command directly."""
    infra_service.terraform_command(command, list(arguments), with_vars=with_vars)
