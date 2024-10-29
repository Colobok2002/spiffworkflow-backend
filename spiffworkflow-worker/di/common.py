"""
:mod:`common` -- Общие компоненты
===================================
.. moduleauthor:: Afanasev Nikita <n-afanacev@it-serv.ru>
"""
from logging import Logger
from typing import Optional

from dependency_injector import containers, providers
from iserv.helpers.pytracelog import extend_log_record, get_logger
from iserv.helpers.pytracelog.handlers import LogstashHandler, StderrHandler, StdoutHandler
from iserv.helpers.pytracelog.handlers import TracerHandler
from iserv.helpers.pytracelog.trace import JaegerExporter, init_exporter

__all__ = ("CommonDI",)


def init_logger(
        env_id: str,
        loglevel: str,
        app_name: str,
        app_ver: str,
        logstash_host: str = None,
        logstash_port: int = 5959,
        logstash_index: Optional[str] = None,
) -> Logger:
    """
    Инициализация логгера

    :param env_id: Идентификатор окружения
    :param loglevel: Уровень логирования
    :param app_name: Наименование приложения
    :param app_ver: Версия приложения
    :param logstash_host: Адрес Logstash сервера
    :param logstash_port: Порт Logstash сервера
    :param logstash_index: Индекс, в который будет выгружен лог
    """
    if not logstash_index:
        logstash_index = "pybeat"

    logger = get_logger(app_name)

    extend_log_record(env_id=env_id, app_name=app_name, app_ver=app_ver)

    logger.setLevel(level=loglevel.upper())

    logger.addHandler(StdoutHandler())
    logger.addHandler(StderrHandler())

    if logstash_host:
        logger.addHandler(
            LogstashHandler(
                host=logstash_host,
                port=int(logstash_port),
                index_name=logstash_index,
            )
        )

    return logger


def init_tracing(
        env_id: str,
        service_name: str,
        service_ver: str,
        logger: Logger,
        jaeger_host: str = None,
        jaeger_port: int = 6831,
        udp_split_oversized_batches: bool = True,
) -> None:
    """
    :param env_id: Идентификатор окружения
    :param service_name: Наименование сервиса
    :param service_ver: Версия сервиса
    :param jaeger_host: Адрес сервера Jaeger
    :param jaeger_port: Порт сервера Jaeger
    :param udp_split_oversized_batches: Разделять UPD пакеты, превышающие максимальную длину
    :param logger: Логгер
    """
    if jaeger_host:
        init_exporter(
            service_name=service_name,
            tags={
                "env_id": env_id,
                "service_ver": service_ver,
            },
            exporter=JaegerExporter(
                agent_host_name=jaeger_host,
                agent_port=int(jaeger_port),
                udp_split_oversized_batches=udp_split_oversized_batches,
            ),
        )

        logger.addHandler(TracerHandler())


class CommonDI(containers.DeclarativeContainer):
    """Контейнер для инициализации общих объектов"""

    config = providers.Configuration()

    logger = providers.Resource(
        init_logger,
        env_id=config.env_id,
        loglevel=config.loglevel,
        app_name=config.app_name,
        app_ver=config.app_ver,
        logstash_host=config.logstash.host,
        logstash_port=config.logstash.port,
        logstash_index=config.logstash.index,
    )

    _ = providers.Resource(
        init_tracing,
        env_id=config.env_id,
        service_name=config.app_name,
        service_ver=config.app_ver,
        jaeger_host=config.jaeger.host,
        jaeger_port=config.jaeger.port,
        udp_split_oversized_batches=config.jaeger.udp_split_oversized_batches,
        logger=logger,
    )
