import logging
from typing import Callable, List, Dict

from sqlalchemy import create_engine
from sqlalchemy.engine import Row
from sqlalchemy.orm import sessionmaker, declarative_base, Session

import const

engine = create_engine(const.DB_CONNECTION_URL)
session_factory = sessionmaker(bind=engine)


logging.basicConfig()
logger = logging.getLogger("sqlalchemy.engine")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(const.LOG_FILE_NAME))


Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_factory: Callable[[], Session] = session_factory

    @staticmethod
    def _transform_returning_row_into_dict(r: Row, columns: List[str]) -> Dict:
        result = dict()
        for c in columns:
            result[c] = getattr(r._mapping, c)

        return result

    @staticmethod
    def _transform_select_row_into_dict(r: Row, columns: List[str]) -> Dict:
        result = dict()
        for c in columns:
            result[c] = getattr(r._data[0], c)

        return result
