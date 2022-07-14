import uuid
from typing import List

from pydantic import BaseModel, Field


class HttpError(BaseModel):
    error: str = Field(description="Описание ошибки", example="Не удалось найти адресный объект")


class AoidModel(BaseModel):
    """
    Содержит нормализованный AOID
    """
    aoid: uuid.UUID = Field(description="Нормализованный AOID")


class AoguidModel(BaseModel):
    """
    Содержит нормализованный AOGUID
    """
    aoguid: uuid.UUID = Field(description="Нормализованный AOGUID")


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
