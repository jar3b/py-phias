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
@click.option('-t', type=str, required=True, help='temp folder mounted to Postgres container')
def initdb(f: str, t: str) -> None:
    click.echo(f'Initializing db "{config.pg.host}:{config.pg.port}" from "{f}"')

    # check XML files path
    xml_path = Path(f)
    if not xml_path.exists() or not xml_path.is_dir():
        click.echo(f'"{f}" must be non-empty dir', err=True)
        sys.exit(-1)

    # check temp folder path
    temp_path = Path(t)
    if not temp_path.exists() or not temp_path.is_dir():
        click.echo(f'"{t}" must be non-empty dir', err=True)
        sys.exit(-1)

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create(xml_path, temp_path))
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(e)
        sys.exit(-2)


# @click.command()
# def dropdb():
#     click.echo('Dropped the database')


cli.add_command(initdb)
# cli.add_command(dropdb)

if __name__ == '__main__':
    cli()
