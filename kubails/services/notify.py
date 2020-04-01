import click
import logging
import os
from typing import Dict
from kubails.external_services import gcloud, slack
from kubails.services import config_store
from kubails.utils.service_helpers import get_codebase_subfolder, sanitize_name


logger = logging.getLogger(__name__)

NOTIFIER_FOLDER = "build_notifier"

# This is the PubSub topic that the notifier is triggered on.
NOTIFIER_TRIGGER = "cloud-builds"

# Theses values are taken from 'resources/build_notifier/index.js'.
SLACK_FAILURE_NOTIFIER_ENTRYPOINT = "slackFailureNotifier"
GITHUB_NOTIFIER_ENTRYPOINT = "githubNotifier"
BITBUCKET_NOTIFIER_ENTRYPOINT = "bitbucketNotifier"


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
        self._deploy_notifier(
            notifier_name="slack-failure-notifier",
            notifier_entrypoint=SLACK_FAILURE_NOTIFIER_ENTRYPOINT,
            env_vars={"SLACK_WEBHOOK": slack_webhook},
            repo_name=repo_name
        )

    def deploy_github_notifier(self, access_token: str, repo_name: str = None) -> None:
        self._deploy_notifier(
            notifier_name="github-notifier",
            notifier_entrypoint=GITHUB_NOTIFIER_ENTRYPOINT,
            env_vars={"GITHUB_ACCESS_TOKEN": access_token},
            repo_name=repo_name
        )

    def deploy_bitbucket_notifier(self, access_token: str, user: str, repo_name: str = None) -> None:
        self._deploy_notifier(
            notifier_name="bitbucket-notifier",
            notifier_entrypoint=BITBUCKET_NOTIFIER_ENTRYPOINT,
            env_vars={
                "BITBUCKET_ACCESS_TOKEN": access_token,
                "BITBUCKET_USER": user,
            },
            repo_name=repo_name
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

    def _deploy_notifier(
        self,
        notifier_name: str = "",
        notifier_entrypoint: str = "",
        env_vars: Dict[str, str] = {},
        repo_name: str = None
    ) -> None:
        if not repo_name:
            # Yes, the repo is assumed to just be the project_name.
            # This is also true for the Terraform configs.
            # TODO: This should probably be changed at some point.
            repo_name = self.config.project_name

        notifier_source = os.path.join(get_codebase_subfolder("resources"), NOTIFIER_FOLDER)

        self.gcloud.deploy_function(
            "{}-{}".format(repo_name, notifier_name),
            notifier_source,
            entrypoint=notifier_entrypoint,
            trigger=NOTIFIER_TRIGGER,
            env_vars={**env_vars, "TARGET_REPO": repo_name}
        )
