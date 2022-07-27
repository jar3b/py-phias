import uuid
from typing import List, Type

from aiohttp_pydantic.oas.typing import r404, r422, r500, r504
from pydantic import BaseModel, Field


def error(code: int) -> Type[BaseModel]:
    class HttpError(BaseModel):
        error: str = Field(
            description="Описание ошибки",
            example={
                400: "Invalid input text",
                404: "Не удалось найти адресный объект",
                422: "aoid: value is not a valid uuid",
                500: "Internal server error",
                504: "Gateway timeout"
            }.get(code, 'Internal server error')
        )

    return HttpError


basic_errors = r404[error(404)] | r500[error(500)] | r504[error(504)]
standard_errors = basic_errors | r422[error(422)]


class AoidModel(BaseModel):
    """
    Содержит нормализованный AOID
    """
    aoid: uuid.UUID = Field(description="Нормализованный AOID", example="352e53dd-7645-41e9-a854-28192ca8710b")


class AoguidModel(BaseModel):
    """
    Содержит нормализованный AOGUID
    """
    aoguid: uuid.UUID = Field(description="Нормализованный AOGUID", example="fc22fe8c-bbf6-4428-b728-25cf0cc4b64b")


class AoNameModel(BaseModel):
    """
    Содержит текстовую строку с полным именем адресного объекта
    """
    fullname: str = Field(description="Имя адресного объекта", example="АО Чукотский, р-н Билибинский")


class AoNameListModel(BaseModel):
    """
    Содержит массив из текстовых строк объекта (для совместимости)
    """
    __root__: List[AoNameModel]


class AoElementModel(BaseModel):
    """
    Содержит развернутое описание элемента адресного объекта
    """
    aoid: uuid.UUID = Field(description="AOID", example="13bd73c9-cfb8-418e-ae40-30273ef50d93")
    aoguid: uuid.UUID = Field(description="AOID", example="f136159b-404a-4f1f-8d8d-d169e1374d5c")
    shortname: str = Field(description="Сокращенный тип объекта", example="АО")
    formalname: str = Field(description="Формализованное имя", example="Чукотский")
    aolevel: int = Field(description="Уровень объекта (AOLEVEL)", example=1)
    regioncode: int = Field(description="Код региона в каком-то старом формате", example=87)
    socrname: str = Field(description="Полный тип объекта", example="Автономный округ")


class AoListElementsModel(BaseModel):
    """
    Последовательность элементов для адресного объекта
    """
    __root__: List[AoElementModel]


class AoResultItemModel(BaseModel):
    """
    Описатель найденного варианта адресного объекта
    """
    cort: int = Field(description="Количество несовпавших слов", example=1)
    text: str = Field(description="Полное название адресного объекта",
                      example="обл Псковская, р-н Порховский, д Гречушанка")
    ratio: int = Field(description="Рейтинг совпадения (выше - лучше)", example=1537)
    aoid: uuid.UUID = Field(description="AOID адресного объекта", example="1d6185b5-25a6-4fe8-9208-e7ddd281926a")


class AoResultsModel(BaseModel):
    __root__: List[AoResultItemModel]
