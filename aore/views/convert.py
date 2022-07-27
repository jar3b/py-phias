import uuid
from typing import Union

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200

from aore.schemas import standard_errors, AoguidModel


class ConvertAoidView(PydanticView):
    async def get(self, aoid: uuid.UUID, /, ) -> Union[
        r200[AoguidModel],
        standard_errors
    ]:
        """
        Преобразует AOID в нормализованный AOGUID
        """
        aoguid = await self.request.app['ff'].convert(aoid)

        return web.json_response(text=AoguidModel(aoguid=aoguid).json())
