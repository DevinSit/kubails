import click
import logging
from kubails.services.notify import Notify
from kubails.utils.command_helpers import log_command_args_factory


logger = logging.getLogger(__name__)
log_command_args = log_command_args_factory(logger, "Notify '{}' args")

notify_service = None


@click.group()
def notify():
    global notify_service

    notify_service = Notify()


############################################################
# Slack sub-group
############################################################


@notify.group()
def slack():
    pass


@slack.command()
@click.argument("webhook")
@click.option("--namespace", prompt=True)
@click.option("--commit", prompt=True)
@log_command_args
def success(webhook: str, namespace: str, commit: str) -> None:
    notify_service.send_slack_success_message(webhook, namespace=namespace, commit=commit)


@slack.command()
@click.argument("webhook")
@click.option("--repo")
@log_command_args
def deploy_failure_notifier(webhook: str, repo: str) -> None:
    notify_service.deploy_slack_failure_notifier(webhook, repo_name=repo)
