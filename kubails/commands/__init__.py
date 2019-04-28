import click  # noqa
from typing import List  # noqa
from . import cluster, config, infra, notify, root, service

groups = [cluster.cluster, config.config, infra.infra, notify.notify, service.service]  # type: List[click.Group]
commands = root.root.commands.values()  # type: List[click.Command]
