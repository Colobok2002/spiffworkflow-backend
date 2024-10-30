from argparse import Action
from functools import wraps
from logging import Logger, getLogger
from typing import Any, Dict, List, Optional, Callable
from celery import Celery
from kombu import Exchange, Queue
from celery.signals import worker_init
from celery.exceptions import WorkerShutdown
from kombu import Connection
from spiffworkflowWorker.spiffManager import SpiffworkflowWorkerManager
from celery import shared_task


class CeleryTasks:
    """
    Задачи Celery
    """

    def __init__(
            self,
            celery: Celery,
            exchange: str = 'spiffworkflow-worker',
            logger: Optional[Logger] = None,
            check_interval: int = 10,
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

        self.start_task_queue = Queue(
            name=f'{exchange.name}.start_task',
            exchange=exchange,
            routing_key=f'{exchange.name}.start_task'
        )

        self.check_task_status_queue = Queue(
            name=f'{exchange.name}.check_task_status',
            exchange=exchange,
            routing_key=f'{exchange.name}.check_task_status'
        )

        # Регистрация задач Celery
        self.start_task = self.register_celery_task(self.start_task, queue=self.start_task_queue)
        self.check_task_status = self.register_celery_task(self.check_task_status, queue=self.check_task_status_queue)

        # Регистрация обработчиков событий
        # # Инициализация
        worker_init.connect(self.init)

        self.actions: Optional[Dict[str, str]] = dict()
        self.callback_actions: Optional[Dict[str, str]] = dict()

        self.check_interval = check_interval

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

    def start_task(self, manager: SpiffworkflowWorkerManager) -> None:
        """
        Запуск задачи Spiffworkflow

        :return: None
        """
        self.logger.info(f'Запуск операции start_task', extra={'tags': manager.to_dict()})

        manager.init_process()
        manager.start_process()
        manager.get_tasks_info()

        self.check_task_status.apply_async(args=[manager], queue=self.check_task_status_queue.name)

    def enqueue_start_task(self, manager: SpiffworkflowWorkerManager) -> None:
        """
        Отправляет задачу get_actions в очередь Celery.

        :return: None
        """
        self.logger.info("Отправка задачи start_task в очередь Celery")
        self.start_task.apply_async(args=[manager], queue=self.start_task_queue.name)

    def check_task_status(self, manager: SpiffworkflowWorkerManager) -> None:
        """
        Задача для проверки статуса основной задачи каждые n секунд.
        """

        status = manager.get_task_status()
        self.logger.info(f"Проверка статуса задачи {status}", extra={'tags': manager.to_dict()})

        if status != "COMPLETED" or status != "ERROR":
            self.check_task_status.apply_async(args=[manager],
                                               countdown=self.check_interval, queue=self.check_task_status_queue.name)
        else:
            self.logger.info(f"Задача завершена со статусом: {status}")

    def clear_queues(self) -> None:
        """
        Очищает очереди start_task и check_task_status.
        """

        with Connection(self.celery.conf.broker_url) as conn:
            for queue in [self.start_task_queue, self.check_task_status_queue]:
                with conn.channel() as channel:
                    bound_queue = queue(channel)
                    bound_queue.purge()
                    self.logger.info(f"Очередь '{queue.name}' очищена.")
