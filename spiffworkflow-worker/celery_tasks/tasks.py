from argparse import Action
from functools import wraps
from logging import Logger, getLogger
from typing import Any, Dict, List, Optional, Callable
from celery import Celery
from kombu import Exchange, Queue
from celery.signals import worker_init
from celery.exceptions import WorkerShutdown


class CeleryTasks:
    """
    Задачи Celery
    """

    def __init__(
            self,
            celery: Celery,
            exchange: str = 'spiffworkflow-worker',
            logger: Optional[Logger] = None
    ):
        """
        Конструктор

        :param celery: Менеджер трансформации Jupyter ноутбуков
        :param logger: Менеджер для работы с секретами
        """
        self.celery = celery

        if logger is None:
            logger = getLogger()
        self.logger = logger

        exchange: Exchange = Exchange(name=exchange)

        exec_queue = Queue(
            name=f'{exchange.name}.exec',
            exchange=exchange,
            routing_key=f'{exchange.name}.exec'
        )
        exec_from_cts_queue = Queue(
            name=f'{exchange.name}.exec_from_cts',
            exchange=exchange,
            routing_key=f'{exchange.name}.exec_from_cts'
        )

        self.service_queue = Queue(
            name=f'{exchange.name}.srv',
            exchange=exchange,
            routing_key=f'{exchange.name}.srv'
        )
        # Регистрация задач Celery
        self.get_actions = self.register_celery_task(self.get_actions, queue=self.service_queue)

        # Регистрация обработчиков событий
        # # Инициализация
        worker_init.connect(self.init)

        self.actions: Optional[Dict[str, str]] = dict()
        self.callback_actions: Optional[Dict[str, str]] = dict()

    def init(self, *args, **kwargs) -> None:
        """
        Инициализация приложения:
         * Инициализация рабочей директории;
         * Формирование метаданных операций.
        """

        try:
            self.logger.info('Запуск инициализации Celery')
        except Exception as e:
            msg = 'Ошибка инициализации Celery'
            self.logger.exception(msg)
            raise WorkerShutdown(msg) from e

        self.logger.info('Инициализация Celery завершена успешно')

    def register_celery_task(self, method: Callable, task_name: str = None, **kwargs) -> Callable:
        """
        Регистрация метода класса в качестве задачи Celery (из коробки не работает, т.к. не передается аргумент self)

        :param method: Метод класса, который необходимо зарегистрировать в качестве задачи Celery
        :param task_name: Наименование задачи
        :param kwargs: Аргументы Celery, используемые при регистрации задачи

        :return: Метод, зарегистрированный в качестве задачи Celery
        """
        self.logger.info(f'Регистрация метода {method.__name__} в качестве задачи Celery')

        task_name = task_name or f'{self.__class__.__name__}.{method.__name__}'

        @self.celery.task(name=task_name, **kwargs)
        @wraps(method)
        def wrapper(*a, **kw):
            return method(*a, **kw)

        # Инициализируем маршрутизацию.
        # Этого тоже Celery не умеет из коробки, хотя поддерживает соответствующие параметры при регистрации задачи
        queue = kwargs.get('queue', None)
        if queue is not None:
            if self.celery.conf.task_queues is None:
                self.celery.conf.task_queues = list()
            if self.celery.conf.task_routes is None:
                self.celery.conf.task_routes = dict()

            if queue not in self.celery.conf.task_queues:
                self.celery.conf.task_queues.append(queue)

            self.celery.conf.task_routes[task_name] = {
                'queue': queue.name,
                'routing_key': queue.routing_key
            }

        self.logger.info(f'Регистрация метода в качестве задачи Celery завершена успешно')

        return wrapper

    def get_actions(self) -> None:
        """
        Формирование метаданных о доступных операциях

        :return: Метаинформация о доступных операциях
        """
        self.logger.info('Запуск формирования метаданных о доступных операциях')

        self.logger.info('Формирование метаданных о доступных операциях завершено успешно')

        return None

    def enqueue_get_actions_task(self) -> None:
        """
        Отправляет задачу get_actions в очередь Celery.

        :return: None
        """
        self.logger.info("Отправка задачи get_actions в очередь Celery")
        self.get_actions.apply_async(queue=self.service_queue.name)
