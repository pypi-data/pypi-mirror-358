"""
Command-line interface for SyftWallet
"""

import click
from rich.console import Console
from rich.table import Table
from . import SyftWallet, get, store, list_keys, delete, show_status

console = Console()


@click.group()
@click.version_option()
def main():
    """SyftWallet - Secure key and secret management using 1Password integration"""
    pass


@main.command()
@click.argument('name')
@click.argument('value')
@click.option('--tags', '-t', multiple=True, help='Tags for organization')
@click.option('--description', '-d', help='Description for the secret')
@click.option('--vault', '-v', help='1Password vault name')
def set(name, value, tags, description, vault):
    """Store a secret securely"""
    success = store(name, value, list(tags), description, vault)
    if success:
        console.print(f"[green]✓ Secret '{name}' stored successfully[/green]")
    else:
        console.print(f"[red]✗ Failed to store secret '{name}'[/red]")
        raise click.ClickException("Failed to store secret")


@main.command()
@click.argument('name')
@click.option('--env-var', '-e', help='Environment variable to check as fallback')
def get_secret(name, env_var):
    """Retrieve a secret"""
    value = get(name, env_var)
    if value:
        console.print(f"[green]✓ Retrieved secret '{name}'[/green]")
        console.print(value)
    else:
        console.print(f"[red]✗ Secret '{name}' not found[/red]")
        raise click.ClickException("Secret not found")


@main.command()
@click.option('--vault', '-v', help='1Password vault to list from')
def list_secrets(vault):
    """List all stored secrets"""
    keys = list_keys(vault)
    
    if not keys:
        console.print("[yellow]No secrets found[/yellow]")
        return
    
    table = Table(title=f"Stored Secrets{f' in {vault}' if vault else ''}")
    table.add_column("Name", style="bold cyan")
    table.add_column("Vault", style="blue")
    table.add_column("Tags", style="green")
    table.add_column("Created", style="dim")
    
    for key in keys:
        tags_str = ", ".join(key.get("tags", []))
        table.add_row(
            key.get("name", ""),
            key.get("vault", ""),
            tags_str,
            key.get("created_at", "")
        )
    
    console.print(table)


@main.command()
@click.argument('name')
@click.option('--vault', '-v', help='1Password vault')
@click.confirmation_option(prompt='Are you sure you want to delete this secret?')
def remove(name, vault):
    """Delete a secret"""
    success = delete(name, vault)
    if success:
        console.print(f"[green]✓ Secret '{name}' deleted successfully[/green]")
    else:
        console.print(f"[red]✗ Failed to delete secret '{name}'[/red]")
        raise click.ClickException("Failed to delete secret")


@main.command()
def status():
    """Show wallet status"""
    show_status()


if __name__ == '__main__':
    main()
