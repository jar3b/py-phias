import asyncpg
from aiohttp import web
from aiohttp_pydantic import oas

from . import settings, log
from .search import FiasFactory
from .views import NormalizeAoidView, error_middleware, ExpandAoidView, ConvertAoidView, GetAoidTextView


async def init_fias(app: web.Application) -> None:
    app['ff'] = FiasFactory(app)


async def shutdown_fias(app: web.Application) -> None:
    pass


async def init_pg(app: web.Application) -> None:
    conf = app['config']['pg']
    dsn = 'postgres://{user}:{password}@{host}:{port}/{db}'.format(**conf)
    log.info('Connecting to pg_main (%s:%s)' % (conf['host'], conf['port']))

    app['pg'] = await asyncpg.create_pool(dsn, max_inactive_connection_lifetime=conf['pool_recycle'])


async def shutdown_pg(app: web.Application) -> None:
    await app['pg'].close()


def run(port: int) -> None:
    # create web app and set config
    app = web.Application(middlewares=[
        error_middleware
    ])
    app['config'] = settings.config
    app['name'] = 'fias-api'

    app.on_startup.append(init_pg)
    app.on_cleanup.append(shutdown_pg)

    app.on_startup.append(init_fias)
    app.on_cleanup.append(shutdown_fias)

    app.router.add_view('/normalize/{aoid}', NormalizeAoidView)
    app.router.add_view('/expand/{aoid}', ExpandAoidView)
    app.router.add_view('/aoid2aoguid/{aoid}', ConvertAoidView)
    app.router.add_view('/gettext/{aoid}', GetAoidTextView)

    # --
    # ** OAS (OpenAPI Swagger docs) **
    # --
    oas.setup(app, url_prefix='/docs', raise_validation_errors=True)

    # now run_app using default asyncio loop
    web.run_app(app, port=port)
