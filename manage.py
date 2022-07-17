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
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--pg-temp', type=str, help='temp folder mounted in Postgres container (same as `-t` if not specified)')
def initdb(f: str, t: str, pg_temp: str | None) -> None:
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

    # check if pg-temp specified
    if pg_temp is None:
        click.echo(f"Use pg-temp as `-t` ({t})")
        pg_temp = temp_path

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create(xml_path, temp_path, Path(pg_temp)))
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
