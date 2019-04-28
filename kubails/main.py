import click
from typing import Sequence, Union
from kubails.commands import commands, groups
from kubails.utils.logger import create_logger


VERSION = "0.0.1"
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], max_content_width=180)

logger = create_logger()  # noqa: Create the root logger for submodules to use


def construct_cli(commands: Sequence[Union[click.Command, click.Group]], docstring: str) -> click.Group:
    cli = click.Group(context_settings=CONTEXT_SETTINGS, help=docstring)
    cli = click.version_option(version=VERSION)(cli)

    for command in commands:
        cli.add_command(command)

    for group in groups:
        cli.add_command(group)

    return cli


docstring = "A framework for developing and deploying Kubernetes native applications on Google Cloud Platform."
cli = construct_cli(commands, docstring)


if __name__ == "__main__":
    cli()
