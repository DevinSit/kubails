import click
from typing import Dict
from kubails.services.service import Service
from kubails.templates import SERVICES_CONFIG, SERVICE_TEMPLATES


SERVICE_GENERATION_PROMPTS = {
    "with_index": {
        "service_type": "Choose a template for service {}",
        "subdomain": "Enter a subdomain for service {}",
        "title": "Enter a title for service {}",
        "name": "Enter a name for service {}"
    },
    "without_index": {
        "service_type": "Choose a service template",
        "subdomain": "Enter a subdomain for the service",
        "title": "Enter a title for the service",
        "name": "Enter a name for the service"
    }
}


def build_extra_service_generation_options(service_type: str) -> Dict[str, str]:
    extra_config_options = SERVICES_CONFIG[service_type].extra_config_options
    config_options = {}

    for option in extra_config_options:
        option_value = click.prompt(option["prompt"])
        config_options[option["option_name"]] = option_value

    return config_options


def generate_service(
    service_service: Service,
    # Used when generating a new project (see commands/root.py)
    service_index: int = None,
    # Need these as optional args since they could be specified as command line args
    service_type: str = None,
    subdomain: str = None,
    title: str = None
) -> None:
    prompts = (
        SERVICE_GENERATION_PROMPTS["without_index"] if service_index is None
        else SERVICE_GENERATION_PROMPTS["with_index"]
    )

    if service_type is None:
        service_type = click.prompt(
            prompts["service_type"].format(service_index),
            type=click.Choice(SERVICE_TEMPLATES),
            default=SERVICE_TEMPLATES[0]
        )

    if subdomain is None:
        subdomain = click.prompt(prompts["subdomain"].format(service_index), default="")

    if title is None:
        title = click.prompt(prompts["title"].format(service_index))

    name = click.prompt(
        prompts["name"].format(service_index),
        default=title.lower().replace(" ", "-")
    )

    extra_config = build_extra_service_generation_options(service_type)
    service_service.generate(service_type, title, name, subdomain, extra_config)
