import sys

import environ

from aore.app import run
from settings import AppConfig


def setup_uvloop() -> None:
    try:
        import uvloop
    except:
        print('Cannot use uvloop')
    else:
        print('Using uvloop')
        uvloop.install()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: run <port>')
        sys.exit(-1)

    setup_uvloop()
    config: AppConfig = environ.to_config(AppConfig)

    run(int(sys.argv[1]), config)
