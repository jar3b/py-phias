import uuid
from typing import Union

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r404

from aore.schemas import HttpError, AoNameModel, AoNameListModel


class GetAoidTextView(PydanticView):
    async def get(self, aoid: uuid.UUID, /, ) -> Union[r200[AoNameListModel], r404[HttpError]]:
        """
        Возвращает простую текстовую строку по указанному AOID (при AOGUID будет
        ошибка, так что нужно предварительно нормализовать)
        """
        ao_name = await self.request.app['ff'].gettext(aoid)

        return web.json_response(text=AoNameListModel(__root__=[AoNameModel(fullname=ao_name)]).json())
