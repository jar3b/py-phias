import asyncio
import sys
from pathlib import Path
from typing import Tuple

import click
import environ

from orchestra.db import DbFiller
from orchestra.sphinx import SphinxFiller
from settings import AppConfig

config: AppConfig = environ.to_config(AppConfig)


def _get_temps(local_temp: str, container_temp: str | None) -> Tuple[Path, Path]:
    # check temp folder path
    temp_path = Path(local_temp)
    if not temp_path.exists() or not temp_path.is_dir():
        click.echo(f'Temp folder {temp_path.absolute()} is not exists', err=True)
        sys.exit(-1)

    # check if pg-temp specified
    if container_temp is None:
        container_temp_path = temp_path
    else:
        container_temp_path = Path(container_temp)

    return temp_path, container_temp_path


@click.group()
def cli():
    pass


@click.command()
@click.option('-f', type=str, required=True, help='folder containing unpacked fias_xml.zip')
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--container-temp', type=str, help='temp folder mounted in Postgres container '
                                                 '(same as `-t` if not specified)')
def initdb(f: str, t: str, container_temp: str | None) -> None:
    click.echo(f'Initializing db "{config.pg.host}:{config.pg.port}" from "{f}"')

    # check XML files path
    xml_path = Path(f)
    if not xml_path.exists() or not xml_path.is_dir():
        click.echo(f'"{f}" must be non-empty dir', err=True)
        sys.exit(-1)

    # check temp folder path
    temp_path, container_temp_path = _get_temps(t, container_temp)

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create(xml_path, temp_path, container_temp_path))
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(e)
        sys.exit(-2)


@click.command()
@click.option('-f', type=str, required=True, help='config filename, example="idx_addrobj.conf"')
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--container-temp', type=str, help='temp folder mounted in Postgres container '
                                                 '(same as `-t` if not specified)')
@click.option('--sphinx-var', type=str, required=True, help='Sphinx var directory, example="/var/lib/sphinxsearch"')
def create_addrobj_config(f: str, t: str, container_temp: str | None, sphinx_var: str) -> None:
    # check temp folder path
    temp_path, _ = _get_temps(t, container_temp)

    try:
        filler = SphinxFiller(config)
        filler.create_addrobj_index_conf(f, temp_path, sphinx_var)
        click.echo(
            f'indexer {config.sphinx.index_addrobj} -c {Path(container_temp, f).as_posix()} '
            f'--buildstops {Path(container_temp, "suggdict.txt").as_posix()} 200000 --buildfreqs'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(-2)


cli.add_command(initdb)
cli.add_command(create_addrobj_config)

if __name__ == '__main__':
    cli()
