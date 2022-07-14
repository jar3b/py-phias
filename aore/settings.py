import logging
import os
from typing import Any, Dict


def str2bool(v: str) -> bool:
    return v.lower() in ("yes", "true", "t", "1")


config: Dict[str, Any] = {
    'pg': {
        'host': os.environ.get('PG_HOST', '127.0.0.1'),
        'port': int(os.environ.get('PG_PORT', '5432')),
        'user': os.environ.get('PG_USER', 'fias'),
        'password': os.environ.get('PG_PASS', '<FROM ENV>'),
        'db': os.environ.get('PG_DB_MAIN', 'fias_db'),
        'pool_recycle': float(os.environ.get('PG_POOL_RECYCLE', '30.0'))
    }
}

LOG_LEVEL = logging.DEBUG if str2bool(os.environ.get('APP_DEBUG', '1')) else logging.INFO
