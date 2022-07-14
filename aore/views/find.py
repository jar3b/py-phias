from typing import Union

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r404

from aore.schemas import HttpError, AoResultsModel


class FindAoView(PydanticView):
    async def get(self, text: str, /, strong: bool = False) -> Union[r200[AoResultsModel], r404[HttpError]]:
        """
        Полнотекстовый поиск по названию адресного объекта

        `text` - строка поиска

        `strong` - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток). Строгий используется при
        импорте из внешних систем (автоматически), где ошибка критична

        Если указан параметр `?strong=true` (или `?strong=1`), то в массиве будет один результат, или ошибка. Если же
        флаг не указан (или `false`), то будет выдано 10 наиболее релевантных результатов.
        """
        found_hints = await self.request.app['ff'].find(text, strong)
        return web.json_response(text=AoResultsModel(__root__=found_hints).json())
