import re
from typing import Union

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r400

from aore.exceptions import FiasBadDataException
from aore.schemas import AoResultsModel, basic_errors, error


class FindAoView(PydanticView):
    async def get(self, text: str, /, strong: bool = False) -> Union[
        r200[AoResultsModel],
        r400[error(400)],
        basic_errors
    ]:
        """
        Полнотекстовый поиск по названию адресного объекта

        `text` - строка поиска

        `strong` - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток). Строгий используется при
        импорте из внешних систем (автоматически), где ошибка критична

        Если указан параметр `?strong=true` (или `?strong=1`), то в массиве будет один результат, или ошибка. Если же
        флаг не указан (или `false`), то будет выдано 10 наиболее релевантных результатов.
        """
        if not re.match('^[0-9A-zА-яЁё, .-/]{3,}$', text):
            raise FiasBadDataException('Invalid input text')
        found_hints = await self.request.app['ff'].find(text, strong)
        return web.json_response(text=AoResultsModel(__root__=found_hints).json())
