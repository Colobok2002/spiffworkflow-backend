"""
:mod:`di` -- description
===================================
.. moduleauthor:: Afanasev Nikita <n-afanacev@it-serv.ru>
"""
from os import environ
from pathlib import Path

__all__ = (
    "APPLICATION_CONFIG",
    "APPLICATION_DEFAULT_CONFIG",
)


APPLICATION_CONFIG = environ.get(
    "APPLICATION_CONFIG",
    (Path(__file__).parent / "config" / "config.yml").as_posix(),
)

APPLICATION_DEFAULT_CONFIG = environ.get(
    'APPLICATION_DEFAULT_CONFIG',
    (Path(__file__).parent / "config" / 'default_config.yml').as_posix()
)
