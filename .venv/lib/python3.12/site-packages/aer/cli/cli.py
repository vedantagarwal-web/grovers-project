import click

from aer import __version__


@click.command()
@click.version_option(__version__)
def main():
    click.echo("Hello, World!")
