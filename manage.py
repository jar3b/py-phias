import asyncio
import sys
from pathlib import Path

import click
import environ

from orchestra.db import DbFiller
from settings import AppConfig

config: AppConfig = environ.to_config(AppConfig)


@click.group()
def cli():
    pass


@click.command()
@click.option('-f', type=str, required=True, help='folder containing unpacked fias_xml.zip')
def initdb(f: str) -> None:
    click.echo(f'Initializing db "{config.pg.host}:{config.pg.port}" from "{f}"')

    # check path
    xml_path = Path(f)
    if not xml_path.exists() or not xml_path.is_dir():
        click.echo(f'"{f}" must be non-empty dir', err=True)
        sys.exit(-1)

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create(xml_path))
    except Exception as e:
        click.echo(e)
        sys.exit(-2)


# @click.command()
# def dropdb():
#     click.echo('Dropped the database')


cli.add_command(initdb)
# cli.add_command(dropdb)

if __name__ == '__main__':
    cli()
