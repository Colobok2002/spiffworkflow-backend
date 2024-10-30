"""
:mod:`run` -- Запуск задач Celery
===================================
.. moduleauthor:: Aleksey Guzhin <a-guzhin@it-serv.ru>
"""
from ..di import APPLICATION_CONFIG, APPLICATION_DEFAULT_CONFIG
from ..di.celery import CeleryDI

di = CeleryDI()
di.config.from_yaml(APPLICATION_DEFAULT_CONFIG)
di.config.from_yaml(APPLICATION_CONFIG)
# di.config.app_name.from_value(__appname__)
# di.config.app_ver.from_value(__version__)
di.init_resources()

app = di.celery()

# celery -A spiffworkflowWorker.celery_tasks.run  worker --loglevel=info --autoscale 1,8
