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
@click.option("--namespace", prompt=True, help="The namespace (subdomain) that was deployed to.")
@click.option("--commit", prompt=True, help="The commit SHA of the build.")
@log_command_args
def success(webhook: str, namespace: str, commit: str) -> None:
    """Send a success message to Slack."""
    notify_service.send_slack_success_message(webhook, namespace=namespace, commit=commit)


@slack.command()
@click.argument("webhook")
@click.option("--repo", help="The name of the git repo to forward failures for.")
@log_command_args
def deploy_failure_notifier(webhook: str, repo: str) -> None:
    """
    Deploy a notifier that sends failure messages to Slack for REPO.

    REPO can be left empty or specified as 'all' to send failure notifications for all repos.
    """
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
@click.option("--repo", help="The name of the git repo to forward build statuses to.")
@log_command_args
def deploy_github_notifier(access_token: str, repo: str) -> None:
    """
    Deploy a notifier that sends build statuses to GitHub using ACCESS_TOKEN for REPO.

    REPO can be left empty or specified as 'all' to send failure notifications for all repos.

    Follow
    https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
    to generate a personal access token.

    The token should have only "repo:status" permissions.
    """
    notify_service.deploy_github_notifier(access_token, repo_name=repo)


@git.command()
@click.argument("access_token")
@click.argument("user")
@click.option("--repo", help="The name of the git repo to forward build statuses to.")
@log_command_args
def deploy_bitbucket_notifier(access_token: str, user: str, repo: str) -> None:
    """
    Deploy a notifier that sends build statuses to Bitbucket using ACCESS_TOKEN as USER for REPO.

    REPO can be left empty or specified as 'all' to send failure notifications for all repos.

    Follow https://confluence.atlassian.com/bitbucket/app-passwords-828781300.html
    to generate an access token.

    The token should have only "Read/Write" access to "Repositories".

    USER should be the username that generated this access token.
    """
    notify_service.deploy_bitbucket_notifier(access_token, user, repo_name=repo)
