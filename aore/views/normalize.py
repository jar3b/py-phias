import uuid
from typing import Union

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200

from aore.schemas import AoidModel, standard_errors


class NormalizeAoidView(PydanticView):
    async def get(self, aoid: uuid.UUID, /, ) -> Union[
        r200[AoidModel],
        standard_errors
    ]:
        """
        Нормализует подаваемый AOID или AOGUID в актуальный AOID
        """
        aoid = await self.request.app['ff'].normalize(aoid)

        return web.json_response(text=AoidModel(aoid=aoid).json())
