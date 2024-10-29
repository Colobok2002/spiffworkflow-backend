"""
:mod:`tasks` -- Контейнер для инициализации асинхронных задач Celery
===================================
.. moduleauthor:: Aleksey Guzhin <a-guzhin@it-serv.ru>
"""
from logging import getLogger
from typing import Optional

from dependency_injector import containers, providers
from iserv.helpers.db.sqlalchemy import DBHelper
from iserv.helpers.pytracelog.trace.sqlalchemy import enable_tracing
from sqlalchemy import create_engine

from .common import CommonDI


__all__ = ("ToolsDi",)


def get_db_helper(
        url: str,
        pool_size: int = None,
        max_overflow: int = None
) -> DBHelper:

    pool_size = pool_size or 5
    max_overflow = max_overflow or 10

    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow
    )

    return DBHelper(engine=engine)


def init_db_logger() -> None:
    logger = getLogger("sqlalchemy.engine")
    logger.setLevel("INFO")


def init_db_trace(db_helper: DBHelper, jaeger_host: Optional[str]) -> None:
    """Инициализация трассировки для БД"""
    if jaeger_host:
        enable_tracing(db_helper.engine)


class ToolsDi(containers.DeclarativeContainer):
    """Инициализация иснструменты для работы Proxy"""

    config = providers.Configuration()
    common_di = providers.Container(
        CommonDI,
        config=config,
    )

    db_helper = providers.Resource(
        get_db_helper,
        url=config.db.url,
        pool_size=config.db.pool_size,
        max_overflow=config.db.max_overflow

    )

    # _ = providers.Resource(
    #     init_db_trace,
    #     db_helper=db_helper,
    #     jaeger_host=config.jaeger.host,
    # )
    # __ = providers.Resource(init_db_logger)
