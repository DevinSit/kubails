import click
import logging
import os
from kubails.external_services import gcloud, slack
from kubails.services import config_store
from kubails.utils.service_helpers import get_codebase_subfolder, sanitize_name


logger = logging.getLogger(__name__)

NOTIFIER_FOLDER = "build_notifier"

# This is the PubSub topic that the notifier is triggered on.
NOTIFIER_TRIGGER = "cloud-builds"

# This value is taken from 'resources/build_notifier/index.js'.
# It is the exported function for the slack failure notifier.
SLACK_FAILURE_NOTIFIER_ENTRYPOINT = "slackFailureNotifier"


class Notify:
    def __init__(self):
        self.config = config_store.ConfigStore()

        self.gcloud = gcloud.GoogleCloud(
            self.config.gcp_project_id,
            self.config.gcp_project_region,
            self.config.gcp_project_zone
        )

        self.slack = slack.Slack()

    def deploy_slack_failure_notifier(self, slack_webhook: str, repo_name: str = None) -> None:
        if not repo_name:
            # Yes, the repo is assumed to just be the project_name.
            # This is also true for the Terraform configs.
            # TODO: This should probably be changed at some point.
            repo_name = self.config.project_name

        notifier_name = "{}-slack-failure-notifier".format(self.config.project_name)
        notifier_source = os.path.join(get_codebase_subfolder("resources"), NOTIFIER_FOLDER)

        env_vars = {
            "SLACK_WEBHOOK": slack_webhook,
            "TARGET_REPO": repo_name
        }

        self.gcloud.deploy_function(
            notifier_name,
            notifier_source,
            entrypoint=SLACK_FAILURE_NOTIFIER_ENTRYPOINT,
            trigger=NOTIFIER_TRIGGER,
            env_vars=env_vars
        )

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
