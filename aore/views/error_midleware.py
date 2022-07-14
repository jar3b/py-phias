import asyncio

from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_middlewares import middleware
from pydantic import ValidationError

from aore import log
from aore.exceptions import FiasException


@middleware
async def error_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    try:
        return await handler(request)
    except asyncio.exceptions.CancelledError:
        return web.json_response(status=504, data={"error": 'Gateway timeout'})
    except HTTPNotFound as e:
        return web.json_response(status=404, data={"error": str(e)})
    except ValidationError as e:
        result = ', '.join([f'{err._loc}: {err.exc}' for err in e.raw_errors])  # type: ignore
        return web.json_response(status=422, data={"error": result})
    except FiasException as e:
        return web.json_response(status=e.code, data={"error": str(e)})
    except BaseException as e:
        log.error("Unhandled exception", exc_info=e)
        return web.json_response(status=500, data={"error": 'Internal server error'})
