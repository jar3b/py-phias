import logging
import os

import environ


def str2bool(v: str) -> bool:
    return v.lower() in ("yes", "true", "t", "1")


@environ.config(prefix="")
class AppConfig:
    @environ.config
    class PG:
        name: str = environ.var("fias_db")
        host: str = environ.var("127.0.0.1")
        port: int = environ.var(5432, converter=int)
        user: str = environ.var("fias")
        password: str = environ.var("<FROM ENV>")
        pool_recycle: float = environ.var(30.0, converter=float)

    @environ.config
    class Sphinx:
        listen: str = environ.var("127.0.0.1:9312")
        index_addrobj: str = 'idx_fias_addrobj'
        index_sugg: str = 'idx_fias_sugg'
        min_length_to_star: int = 3
        delta_len: int = 2
        default_rating_delta: int = 2
        regression_coef: float = 0.08
        max_results_count: int = 10
        search_freq_words: bool = True
        suggestions_count = 6
        sphinx_user_uid = 104

        def listen_port(self) -> str:
            if self.listen.startswith('/'):
                return self.listen
            else:
                return self.listen.split(':')[1]

    pg: PG = environ.group(PG)
    sphinx: Sphinx = environ.group(Sphinx)


LOG_LEVEL = logging.DEBUG if str2bool(os.environ.get('APP_DEBUG', '1')) else logging.INFO
