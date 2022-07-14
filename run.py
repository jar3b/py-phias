import sys

from aore.app import run


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
    run(int(sys.argv[1]))
