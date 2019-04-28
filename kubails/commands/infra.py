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
    global infra_service
    global cluster_service

    infra_service = Infra()
    cluster_service = Cluster()


@infra.command()
@log_command_args
def setup() -> None:
    infra_service.setup()


@infra.command()
@click.confirmation_option(
    prompt="This will delete the project's service account and destroy all Terraform state. Are you sure?"
)
@log_command_args
def cleanup() -> None:
    infra_service.cleanup()


@infra.command()
@log_command_args
def authenticate() -> None:
    if not infra_service.authenticate():
        sys.exit(1)


@infra.command()
@log_command_args
def unauthenticate() -> None:
    if not infra_service.unauthenticate():
        sys.exit(1)


@infra.command()
@click.option("--component", type=click.Choice(["all", "builder"]), default="all")
@log_command_args
def deploy(component: str) -> None:
    if component == "all":
        deploy_result = infra_service.deploy()

        if not deploy_result:
            sys.exit(1)

        name_servers = infra_service.get_name_servers()

        logger.info(
            "\nYou should now point the name servers of your domain "
            "to the following before continuing:\n\n{}\n".format(name_servers)
        )

        if click.confirm("Have you changed the name servers?"):
            logger.info("\nContinuing with cluster deployment...\n")
            cluster_service.deploy()
    elif component == "builder":
        infra_service.deploy_builder()
    else:
        logger.error("WTF, how did you even trigger this?")


@infra.command()
@click.confirmation_option(prompt="This will delete all of the project's infrastructure. Are you sure?")
@log_command_args
def destroy() -> None:
    infra_service.destroy()


@infra.command()
@click.argument("command")
@click.argument("arguments", nargs=-1)
@click.option("--with-vars", default=False, is_flag=True)
@log_command_args
def terraform(command: str, arguments: Tuple[str], with_vars: bool) -> None:
    infra_service.terraform_command(command, list(arguments), with_vars=with_vars)
