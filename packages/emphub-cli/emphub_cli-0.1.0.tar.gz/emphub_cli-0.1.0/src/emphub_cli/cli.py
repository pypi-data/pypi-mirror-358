import click
from .commands import run, pull, push, tags, packages


@click.group()
def root():
    pass



def main_cli():
    root.add_command(run)
    root.add_command(pull)
    root.add_command(push)
    root.add_command(tags)
    root.add_command(packages)
    root()