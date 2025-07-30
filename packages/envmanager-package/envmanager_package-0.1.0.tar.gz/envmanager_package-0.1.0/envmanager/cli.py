import click
from .core import EnvManager

@click.group()
def cli():
    """EnvManager CLI to manage .env files."""
    pass

@cli.command()
@click.argument('key')
@click.argument('value')
@click.option('--env', default='.env', help='Path to .env file')
def add(key, value, env):
    "Add or update a key-value pair in the .env file."
    manager = EnvManager(env)
    manager.add(key, value)
    click.echo(f"Added {key}={value} to {env}")

@cli.command()
@click.argument('key')
@click.option('--env', default='.env', help='Path to .env file')
def remove(key, env):
    "Remove a key from the .env file."
    manager = EnvManager(env)
    manager.remove(key)
    click.echo(f"Removed {key} from {env}")

@cli.command()
@click.option('--required', multiple=True, help='Required keys to validate')
@click.option('--env', default='.env', help='Path to .env file')
def validate(required, env):
    "Validate that required keys exist in the .env file."
    manager = EnvManager(env)
    missing = manager.validate(required)
    if missing:
        click.echo(f"Missing keys: {', '.join(missing)}")
    else:
        click.echo("All required keys are present.")

@cli.command()
@click.option('--template', required=True, help='Path to template .env file')
@click.option('--env', default='.env', help='Path to .env file to generate')
def generate(template, env):
    "Generate a .env file from a template."
    manager = EnvManager(env)
    manager.generate_from_template(template)
    click.echo(f"Generated {env} from {template}") 