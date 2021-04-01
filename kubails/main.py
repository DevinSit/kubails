import click
from typing import Sequence, Union
from kubails.commands import commands, groups
from kubails.services import cluster as cluster_service, config_store
from kubails.utils.logger import create_logger
from kubails.utils.service_helpers import sanitize_name


VERSION = "0.0.1"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], max_content_width=180)

logger = create_logger()  # noqa: Create the root logger for submodules to use


def construct_cli(commands: Sequence[Union[click.Command, click.Group]], docstring: str) -> click.Group:
    @click.group(context_settings=CONTEXT_SETTINGS, help=docstring)
    @click.version_option(version=VERSION)
    @click.option("--only-changed-services", is_flag=True)
    @click.option(
        "--all-services-branch",
        help="Pass the branch to override --only-changed-services for new branches and production."
    )
    def cli(only_changed_services: bool, all_services_branch: str):
        if (only_changed_services):
            config = config_store.ConfigStore()
            cluster = cluster_service.Cluster()

            if all_services_branch:
                branch = sanitize_name(all_services_branch)

                if branch == config.production_namespace:
                    logger.info("Using all services: '{}' is production".format(branch))
                    return

                if cluster.is_new_namespace_cloud_build(branch):
                    logger.info("Using all services: '{}' is a new branch".format(branch))
                    return

            config.use_changed_services()

    for command in commands:
        cli.add_command(command)

    for group in groups:
        cli.add_command(group)

    return cli


docstring = "A framework for developing and deploying Kubernetes native applications on Google Cloud Platform."
cli = construct_cli(commands, docstring)


if __name__ == "__main__":
    cli()
