import click
import logging
import os
from typing import List
from kubails.commands import helpers
from kubails.services.service import Service
from kubails.services.templater import Templater
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Root '{}' args")


@click.group()
def root():
    pass


@root.command()
@log_command_args
def new() -> None:
    _generate_new_project()


def _generate_new_project() -> None:
    # Need to get a listing of the current folders to find out what the
    # project folder is called after creating it.
    current_folders = _get_immediate_subdirs()

    Templater.template_primary()

    updated_folders = _get_immediate_subdirs()
    project_folder = list(set(updated_folders) - set(current_folders))[0]

    # Change to the project folder to be able to instantiate the Service service
    os.chdir(project_folder)
    service_service = Service()

    print("")  # New line for output

    number_of_services = click.prompt("How many services does this project need?", type=int)
    print("")

    if number_of_services <= 0:
        logger.info("Well then, no services for you. Enjoy your service-less project! Exiting.")
        return

    for i in range(number_of_services):
        helpers.generate_service(service_service, service_index=i+1)
        print("")


def _get_immediate_subdirs() -> List[str]:
    return [name for name in os.listdir(".") if os.path.isdir(os.path.join(".", name))]
