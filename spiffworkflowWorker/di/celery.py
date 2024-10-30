"""
:mod:`celery` -- Контейнер для инициализации Celery
===================================
.. moduleauthor:: Aleksey Guzhin <a-guzhin@it-serv.ru>
"""
from logging import Logger
from typing import Optional

from celery import Celery
from dependency_injector import containers, providers
from iserv.helpers.pytracelog.handlers import TracerHandler
from iserv.helpers.pytracelog.trace.celery import enable_tracing
from kombu import Exchange
from spiffworkflowWorker.celery_tasks.tasks import CeleryTasks
from .common import CommonDI

__all__ = ("CeleryDI",)


def init_celery_app(main: str, broker: str, backend: str) -> Celery:
    """
    Инициализация приложения Celery с сериализатором `pickle`

    :param main: Наименование приложения
    :param broker: Брокер сообщений
    :param backend: Хранилище результатов выполнения задач Celery

    :return: Экземпляр :class:`Celery`
    """
    celery = Celery(main, broker=broker, backend=backend)

    celery.conf.task_serializer = "pickle"
    celery.conf.result_serializer = "pickle"
    celery.conf.accept_content = [
        "application/json",
        "application/x-python-serialize",
    ]
    return celery


def init_tracing(
        jaeger_host: str = None, attach_log: bool = False, logger: Optional[Logger] = None
) -> None:
    """
    Инициализация трасировки Celery

    :param jaeger_host: Адрес сервера Jaeger
    :param attach_log: Прикладывать записи лога к Span'ам
    :param logger: Логгер
    """
    if jaeger_host:
        if logger is not None and attach_log:
            logger.addHandler(TracerHandler())

        enable_tracing(worker=False)


def init_exchange(name: Optional[str] = None) -> Exchange:
    name = name or 'PgQ_AW'
    return Exchange(name=name)


class CeleryDI(containers.DeclarativeContainer):
    """Контейнер для инициализации Celery"""

    config = providers.Configuration()
    common_di = providers.Container(CommonDI, config=config)

    exchange = providers.Factory(
        init_exchange,
        name=config.celery.exchange,
    )

    celery = providers.Singleton(
        init_celery_app,
        main=config.app_name,
        broker=config.celery.broker,
        backend=config.celery.backend,
    )

    tasks = providers.Resource(
        CeleryTasks,
        celery=celery,
        logger=common_di.logger,
    )

    _ = providers.Resource(
        init_tracing,
        jaeger_host=config.jaeger.host,
        attach_log=config.jaeger.attach_log,
        logger=common_di.logger,
    )
