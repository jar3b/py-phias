import asyncio
import os
import sys
from pathlib import Path
from typing import Tuple

import click
import environ

from aore.utils import trigram
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
def cli() -> None:
    pass


@click.command()
@click.option('-f', type=str, required=True,
              help='folder containing unpacked fias_xml.zip or zip file with pre-built csv')
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--container-temp', type=str,
              help='temp folder mounted in Postgres container (same as `-t` if not specified)')
def initdb(f: str, t: str, container_temp: str | None) -> None:
    click.echo(f'Initializing db "{config.pg.host}:{config.pg.port}" from "{f}"')

    # check temp folder path
    temp_path, container_temp_path = _get_temps(t, container_temp)

    # check XML files path
    xml_path = Path(f)
    if not xml_path.exists() or not xml_path.is_dir():
        click.echo(f'"{f}" must be non-empty dir', err=True)
        sys.exit(-1)

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create(xml_path, temp_path, container_temp_path))
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(e)
        sys.exit(-2)


@click.command()
@click.option('-f', type=str, required=True, help='folder containing unpacked fias_xml.zip')
@click.option('--target', type=str, required=True, help='target file, like fias_csv.zip')
def create_fias_csv(f: str, target: str) -> None:
    # check XML files path
    xml_path = Path(f)
    if not xml_path.exists() or not xml_path.is_dir():
        click.echo(f'"{f}" must be non-empty dir', err=True)
        sys.exit(-1)

    target_path = Path(target)
    if not target_path.parent.is_dir():
        click.echo(f'{target_path.parent} must be directory')
        sys.exit(-1)

    if target_path.is_file():
        os.remove(target_path)

    try:
        filler = DbFiller(config)
        asyncio.run(filler.create_csv_zip(xml_path, target_path))
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(e)
        sys.exit(-2)


@click.command()
@click.option('-f', type=str, required=True, help='config filename, example="idx_addrobj.conf"')
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--container-temp', type=str, help='temp folder mounted in Sphinx container '
                                                 '(same as `-t` if not specified)')
@click.option('--sphinx-var', type=str, required=True, help='Sphinx var directory, example="/var/lib/sphinxsearch"')
def create_addrobj_config(f: str, t: str, container_temp: str | None, sphinx_var: str) -> None:
    # check temp folder path
    temp_path, container_temp_path = _get_temps(t, container_temp)

    try:
        filler = SphinxFiller(config)
        filler.create_addrobj_index_conf(f, temp_path, sphinx_var)
        click.echo(
            f'indexer {config.sphinx.index_addrobj} -c {Path(container_temp_path, f).as_posix()} '
            f'--buildstops {Path(container_temp_path, "suggdict.txt").as_posix()} 200000 --buildfreqs'
        )
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(-2)


@click.command()
@click.option('-f', type=str, required=True, help='name of suggdict.csv file')
@click.option('-t', type=str, required=True, help='temp folder in app container')
@click.option('--container-temp', type=str, help='temp folder mounted in Postgres container '
                                                 '(same as `-t` if not specified)')
def init_trigram(f: str, t: str, container_temp: str | None) -> None:
    # check temp folder path
    temp_path, container_temp_path = _get_temps(t, container_temp)

    try:
        # parse txt into csv
        txt_file_path = Path(temp_path, f)
        csv_file_path = Path(temp_path, 'suggdict.csv')

        csv_counter = 0
        with txt_file_path.open('r', encoding="utf-8") as dict_file, \
                csv_file_path.open("w", encoding="utf-8") as exit_file:
            while True:
                line = dict_file.readline()
                if line == '':
                    break

                csv_counter += 1
                splitting_seq = line.split(' ')
                keyword = splitting_seq[0]
                freq = splitting_seq[1].rstrip('\n')
                if not keyword or not freq:
                    raise Exception(f'Cannot process {txt_file_path}, invalid line {line}')

                exit_file.write("\t".join([keyword, trigram(keyword), freq]) + "\n")

        click.echo(f'Got {csv_file_path} with {csv_counter} items')

        # write csv into DB
        filler = DbFiller(config)
        asyncio.run(filler.create_table_from_csv(container_temp_path, csv_file_path, "AOTRIG"))

        os.remove(txt_file_path)
        os.remove(csv_file_path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        click.echo(e)
        sys.exit(-2)


@click.command()
@click.option('-f', type=str, required=True, help='config output filename, example="/etc/sphinxsearch/sphinx.conf"')
@click.option('--sphinx-var', type=str, required=True, help='Sphinx var directory, example="/var/lib/sphinxsearch"')
def create_sphinx_config(f: str, sphinx_var: str) -> None:
    try:
        filler = SphinxFiller(config)
        filler.create_sphinx_conf(Path(f), sphinx_var)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(-2)


# public
cli.add_command(initdb)
cli.add_command(create_addrobj_config)
cli.add_command(init_trigram)
cli.add_command(create_sphinx_config)
# internal
cli.add_command(create_fias_csv)

if __name__ == '__main__':
    cli()
