"""Initialize user configuration for cli-git."""

from typing import Annotated

import typer

from cli_git.utils.config import ConfigManager
from cli_git.utils.gh import (
    GitHubError,
    check_gh_auth,
    get_current_username,
    get_user_organizations,
    run_gh_auth_login,
)
from cli_git.utils.validators import ValidationError, validate_prefix, validate_slack_webhook_url


def mask_webhook_url(url: str) -> str:
    """Mask Slack webhook URL for display.

    Args:
        url: Slack webhook URL to mask

    Returns:
        Masked URL for display
    """
    if not url:
        return ""

    # https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX
    # -> https://hooks.slack.com/services/XXX.../XXX.../XXX...
    parts = url.split("/")
    if len(parts) >= 7 and "hooks.slack.com" in url:
        # Mask the tokens (parts[4] = T..., parts[5] = B..., parts[6] = XXX...)
        parts[4] = parts[4][:3] + "..." if len(parts[4]) > 3 else parts[4]
        parts[5] = parts[5][:3] + "..." if len(parts[5]) > 3 else parts[5]
        parts[6] = parts[6][:3] + "..." if len(parts[6]) > 3 else parts[6]
    return "/".join(parts)


def init_command(
    force: Annotated[bool, typer.Option("--force", "-f", help="Force reinitialization")] = False,
) -> None:
    """Initialize cli-git configuration with GitHub account information."""
    # Check gh CLI authentication first
    if not check_gh_auth():
        typer.echo("🔐 GitHub CLI is not authenticated")
        if typer.confirm("Would you like to login now?", default=True):
            typer.echo("📝 Starting GitHub authentication...")
            if run_gh_auth_login():
                typer.echo("✅ GitHub authentication successful!")
            else:
                typer.echo("❌ GitHub login failed")
                raise typer.Exit(1)
        else:
            typer.echo("   Please run: gh auth login")
            raise typer.Exit(1)

    # Get current GitHub username
    try:
        username = get_current_username()
    except GitHubError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(1)

    # Initialize config manager
    config_manager = ConfigManager()
    config = config_manager.get_config()

    # Check if already initialized
    if config["github"]["username"] and not force:
        typer.echo("⚠️  Configuration already exists")
        typer.echo(f"   Current user: {config['github']['username']}")
        if config["github"]["default_org"]:
            typer.echo(f"   Default org: {config['github']['default_org']}")
        typer.echo("   Use --force to reinitialize")
        return

    # Get user organizations
    try:
        orgs = get_user_organizations()
        if orgs:
            typer.echo("\n📋 Your GitHub organizations:")
            for i, org in enumerate(orgs, 1):
                typer.echo(f"   {i}. {org}")
            typer.echo("   0. No organization (use personal account)")

            # Ask for organization selection
            while True:
                choice = typer.prompt("\nSelect organization number", default="0")
                try:
                    choice_num = int(choice)
                    if choice_num == 0:
                        default_org = ""
                        break
                    elif 1 <= choice_num <= len(orgs):
                        default_org = orgs[choice_num - 1]
                        break
                    else:
                        typer.echo("Invalid choice. Please try again.")
                except ValueError:
                    typer.echo("Please enter a number.")
        else:
            typer.echo("\n📋 No organizations found. Using personal account.")
            default_org = ""
    except GitHubError:
        # Fallback to manual input
        default_org = typer.prompt("\nDefault organization (optional)", default="")

    # Ask for Slack webhook URL
    typer.echo("\n🔔 Slack Integration (optional)")
    typer.echo("   Enter webhook URL to receive sync failure notifications")
    while True:
        slack_webhook_url = typer.prompt("Slack webhook URL (optional)", default="")
        try:
            validate_slack_webhook_url(slack_webhook_url)
            break
        except ValidationError as e:
            typer.echo(str(e))
            typer.echo("   Press Enter to skip or enter a valid URL")

    # Ask for default mirror prefix
    while True:
        default_prefix = typer.prompt("\nDefault mirror prefix", default="mirror-")
        try:
            validate_prefix(default_prefix)
            break
        except ValidationError as e:
            typer.echo(str(e))

    # Update configuration
    updates = {
        "github": {
            "username": username,
            "default_org": default_org,
            "slack_webhook_url": slack_webhook_url,
        },
        "preferences": {"default_prefix": default_prefix},
    }
    config_manager.update_config(updates)

    # Success message
    typer.echo()
    typer.echo("✅ Configuration initialized successfully!")
    typer.echo(f"   GitHub username: {username}")
    if default_org:
        typer.echo(f"   Default organization: {default_org}")
    if slack_webhook_url:
        typer.echo(f"   Slack webhook: {mask_webhook_url(slack_webhook_url)}")
    typer.echo(f"   Mirror prefix: {default_prefix}")
    typer.echo()
    typer.echo("Next steps:")
    typer.echo("- Run 'cli-git info' to see your configuration")
    typer.echo("- Run 'cli-git private-mirror <repo-url>' to create your first mirror")
