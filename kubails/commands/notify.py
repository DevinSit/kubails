import click
import logging
from kubails.services.notify import Notify
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Notify '{}' args")

notify_service = None


@click.group()
def notify():
    """Manage notifications for your build pipeline."""
    global notify_service

    notify_service = Notify()


############################################################
# Slack sub-group
############################################################


@notify.group()
def slack():
    """Manage Slack notifications."""
    pass


@slack.command()
@click.argument("webhook")
@click.option("--namespace", prompt=True)
@click.option("--commit", prompt=True)
@log_command_args
def success(webhook: str, namespace: str, commit: str) -> None:
    """Send a success message to Slack."""
    notify_service.send_slack_success_message(webhook, namespace=namespace, commit=commit)


@slack.command()
@click.argument("webhook")
@click.option("--repo")
@log_command_args
def deploy_failure_notifier(webhook: str, repo: str) -> None:
    """Deploy a notifier that sends failure messages to Slack."""
    notify_service.deploy_slack_failure_notifier(webhook, repo_name=repo)


############################################################
# Git sub-group
############################################################


@notify.group()
def git():
    """Manage Git hosting provider build statuses."""
    pass


@git.command()
@click.argument("access_token")
@click.option("--repo")
@log_command_args
def deploy_github_notifier(access_token: str, repo: str) -> None:
    """Deploy a notifier that sends build statuses to GitHub."""
    notify_service.deploy_github_notifier(access_token, repo_name=repo)


@git.command()
@click.argument("access_token")
@click.argument("user")
@click.option("--repo")
@log_command_args
def deploy_bitbucket_notifier(access_token: str, user: str, repo: str) -> None:
    """Deploy a notifier that sends build statuses to Bitbucket."""
    notify_service.deploy_bitbucket_notifier(access_token, user, repo_name=repo)
