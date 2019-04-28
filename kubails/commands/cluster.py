import click
import logging
import os
import sys
from typing import Tuple
from kubails.services.cluster import Cluster
from kubails.services.kube_git_syncer import KubeGitSyncer
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Cluster '{}' args")

cluster_service = None
kube_git_syncer_service = None


@click.group()
def cluster():
    global cluster_service
    global kube_git_syncer_service

    cluster_service = Cluster()
    kube_git_syncer_service = KubeGitSyncer()


@cluster.command()
@log_command_args
def authenticate() -> None:
    cluster_service.authenticate()


@cluster.command()
@click.confirmation_option(prompt="This will delete your project's cluster. Are you sure?")
@log_command_args
def destroy() -> None:
    cluster_service.destroy()


@cluster.command()
@log_command_args
def cleanup_namespaces() -> None:
    kube_git_syncer_service.cleanup_namespaces()


############################################################
# Manifests sub-group
############################################################

DEFAULT_NAMESPACE = "default"
DEFAULT_TAG = "latest"


@cluster.group()
def manifests():
    pass


@manifests.command()
@click.argument("service", nargs=-1)
@click.option("--namespace", default=DEFAULT_NAMESPACE)
@click.option("--tag", default=DEFAULT_TAG)
@log_command_args
def generate(service: Tuple[str], tag: str, namespace: str) -> None:
    if not cluster_service.generate_manifests(list(service), tag, namespace):
        sys.exit(1)


@manifests.command(name="deploy")
@click.argument("service", nargs=-1)
@click.option("--namespace", default=DEFAULT_NAMESPACE)
@log_command_args
def manifests_deploy(service: Tuple[str], namespace: str) -> None:
    if not cluster_service.deploy_manifests(list(service), namespace):
        sys.exit(1)


############################################################
# Secrets sub-group
############################################################

@cluster.group()
def secrets():
    pass


@secrets.command(name="deploy")
@click.argument("service", nargs=-1)
@click.option("--namespace", default=DEFAULT_NAMESPACE)
@log_command_args
def secrets_deploy(service: Tuple[str], namespace: str) -> None:
    if not cluster_service.deploy_secrets(list(service), namespace):
        sys.exit(1)


def _get_service_from_folder() -> str:
    current_dir = os.getcwd()
    parent_dir = os.path.basename(os.path.dirname(current_dir))

    return os.path.basename(current_dir) if parent_dir == "services" else ""


@secrets.command()
@click.argument("file-path", type=click.Path(exists=True))
@click.option("--service", prompt=True, default=_get_service_from_folder())
@click.option(
    "--secret-name",
    prompt=True,
    # This assumes that the user would run this command in the folder for
    # a service (since that's where a secrets file would normally be).
    default=lambda: "{}-secrets".format(os.path.basename(os.getcwd()))
)
@log_command_args
def create(file_path: str, service: str, secret_name: str) -> None:
    if not service:
        logger.error("Service name required.")
        raise click.Abort()

    if not secret_name:
        logger.error("Secret name required.")
        raise click.Abort()

    cluster_service.create_secret(file_path, service, secret_name)
