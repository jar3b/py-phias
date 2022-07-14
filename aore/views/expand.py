import uuid
from typing import Union, List

from aiohttp import web
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200, r404

from aore.schemas import HttpError, AoElementModel, AoListElementsModel


class ExpandAoidView(PydanticView):
    async def get(self, aoid: uuid.UUID, /, ) -> Union[r200[AoListElementsModel], r404[HttpError]]:
        """
        Разворачивает AOID в представление (перед этим нормализует)
        """
        expanded: List[AoElementModel] = await self.request.app['ff'].expand(aoid)

        return web.json_response(text=AoListElementsModel(__root__=expanded).json())
