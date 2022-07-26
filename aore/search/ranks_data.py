import json
from collections import ChainMap

from pydantic import BaseModel


class RanksData(BaseModel):
    freq: int | None
    cnt_socr_like: int
    cnt_socr: int
    scname: str | None
    cnt_exact: int
    cnt_like: int

    @property
    def rank(self) -> str:
        # Формируем список найденных величин совпадений:
        # result[x]
        # x = 0, поиск по неполному совпадению (лайк*), и по длине строки больше исходной, cnt_like
        # x = 1, поиск по точному совпадению, cnt_exact
        # x = 2, поиск по базе сокращений (по полному), cnt_socr
        # x = 3, то же, но по краткому, cnt_socr_like
        return ''.join([
            'x' if self.cnt_like >= 5 else str(self.cnt_like),  # TODO: need to adjust "5"
            'x' if self.cnt_exact > 1 else str(self.cnt_exact),
            'x' if self.cnt_socr > 1 else str(self.cnt_socr),
            'x' if self.cnt_socr_like > 1 else str(self.cnt_socr_like),
        ])

    @classmethod
    def load(cls, s: str) -> 'RanksData':
        # сшивает строку типа
        # "[{"cnt_like" : 1}, {"cnt_exact" : 1}, {"cnt_socr" : 0, "scname" : null}, {"cnt_socr_like" : 0},
        # {"freq" : 200}]"
        # в словарь вроде
        # {'freq': 200, 'cnt_socr_like': 0, 'cnt_socr': 0, 'scname': None, 'cnt_exact': 1, 'cnt_like': 1}
        # и оборачивает его в объект RanksData
        return cls(**dict(ChainMap(*json.loads(s))))

    @property
    def is_freq(self) -> bool:
        return self.freq is not None and self.freq > 30000
