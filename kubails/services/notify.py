import click
import logging
from kubails.external_services import slack
from kubails.services import config_store
from kubails.utils.service_helpers import sanitize_name


logger = logging.getLogger(__name__)


class Notify:
    def __init__(self):
        self.config = config_store.ConfigStore()
        self.slack = slack.Slack()

    def send_slack_success_message(
        self,
        webhook: str,
        namespace: str = "",
        commit: str = ""
    ) -> None:
        if not webhook:
            logger.error("Missing webhook.")
            raise click.Abort()

        domain = self.config.domain
        namespace = sanitize_name(namespace)

        if namespace and namespace == self.config.production_namespace:
            fields = [
                {
                    "title": "Production",
                    "value": "https://{}".format(domain)
                }
            ]
        else:
            fields = [
                {
                    "title": "Branch",
                    "value": "https://{}.{}".format(namespace, domain)
                },
                {
                    "title": "Commit",
                    "value": "https://{}-{}.{}".format(commit, namespace, domain)
                }
            ]

        self.slack.send_message(
            webhook,
            title="Cluster Deployment Completed",
            fields=fields,
            color="good"
        )
