import asyncio
from typing import Dict

from aiohttp import web
from aiohttp.typedefs import Handler
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_middlewares import middleware
from pydantic import ValidationError

from aore import log
from aore.exceptions import FiasException


def get_cors(origin: str, method: str) -> Dict[str, str]:
    if not origin:
        return {}

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': ', '.join(["OPTIONS", method]),
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': '*'
    }


@middleware
async def error_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    cors = get_cors(request.headers.get('origin', ''), request.method)
    try:
        return await handler(request)
    except asyncio.exceptions.CancelledError:
        return web.json_response(status=504, data={"error": 'Gateway timeout'}, headers=cors)
    except HTTPNotFound as e:
        return web.json_response(status=404, data={"error": str(e)}, headers=cors)
    except ValidationError as e:
        result = ', '.join([f'{err._loc}: {err.exc}' for err in e.raw_errors])  # type: ignore
        return web.json_response(status=422, data={"error": result}, headers=cors)
    except FiasException as e:
        return web.json_response(status=e.code, data={"error": str(e)}, headers=cors)
    except BaseException as e:
        log.error("Unhandled exception", exc_info=e)
        return web.json_response(status=500, data={"error": 'Internal server error'}, headers=cors)


@middleware
async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    response = await handler(request)
    if request.headers.get('Origin', ''):
        response.headers.update(get_cors(request.headers.get('Origin', ''), request.method))

    return response
