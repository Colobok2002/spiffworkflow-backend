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
di.init_resources()

app = di.celery()
