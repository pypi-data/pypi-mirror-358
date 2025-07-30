import click
import os
from tabulate import tabulate
from .operations import pullPackage, pushPackage, getConfig
from .func import sizeof_fmt
from .miniohelpers import getClient


CONFIG_PATH = os.path.expanduser("~/.emp/config.yaml")


@click.command()
@click.argument("package")
@click.option("--device", "-d", help="Device to program.")
def run():
    click.echo("Running the package")


@click.command()
@click.argument("package")
def pull(package):
    if ":" in package:
        package, tag = package.split(":")
    else:
        tag = "latest"
    click.echo("Pulling {}:{}...".format(package, tag))
    obj, delta = pullPackage(package, tag, getConfig(CONFIG_PATH))
    click.echo("Downloaded package ({}) in {}s".format(
        sizeof_fmt(obj.size), delta.total_seconds()
    ))


@click.command()
@click.argument("package")
@click.option("--path", "-p", type=click.Path(exists=True))
def push(package, path=None):
    if ":" in package:
        package, tag = package.split(":")
    else:
        tag = "latest"
    config = getConfig(CONFIG_PATH)
    if not path:
        path = "{}/{}/{}/package.tgz".format(
            os.path.expanduser(config["local-storage"]["path"]),
            package, tag
        )
    click.echo("Pushing {}:{} to registry...".format(package, tag))
    size, delta = pushPackage(package, tag, path, config)
    click.echo("Uploaded package ({}) in {}s".format(
        sizeof_fmt(size), delta.total_seconds()
    ))


@click.command()
@click.argument("package")
def tags(package):
    config = getConfig(CONFIG_PATH)
    client = getClient(config)
    bucket = config["registry"]["bucket"]
    objects = list(client.list_objects(bucket, prefix="{}/".format(package)))
    if len(objects) > 0:
        tags_table = []
        click.echo("Tags for {}:".format(package))
        for obj in objects:
            stats = client.stat_object(bucket, obj.object_name+"package.tgz")
            tags_table.append([
                obj.object_name.split("/")[1],
                sizeof_fmt(stats.size),
                stats.last_modified
            ])
        click.echo(
            tabulate(tags_table, headers=["Tag", "Size", "Last Modified"]))


@click.command()
def packages():
    config = getConfig(CONFIG_PATH)
    client = getClient(config)
    bucket = config["registry"]["bucket"]
    objects = list(client.list_objects(bucket))
    if len(objects) > 0:
        click.echo("Packages available on emphub:")
        for obj in objects:
            click.echo("  - {}".format(obj.object_name[:-1]))
