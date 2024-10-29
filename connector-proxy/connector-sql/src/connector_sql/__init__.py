'''
:mod:`__init__` -- Шаблон коннектора для sql операий в pg
===================================
.. moduleauthor:: ilya Barinov (i-barinov@it-serv.ru)
'''


from typing import Any
from connector_sql.di import APPLICATION_CONFIG, APPLICATION_DEFAULT_CONFIG
from connector_sql.di.tools import ToolsDi
from spiffworkflow_backend.spiffworkflow_connector_command.command_interface import CommandErrorDict, ConnectorCommand, ConnectorProxyResponseDict


class SqlConnector(ConnectorCommand):

    def __init__(self, sql_query: str, conect_url: str | None = None,):
        self.tools = ToolsDi()
        self.sql_query = sql_query

        self.tools.config.app_name.from_value(f"SqlScalar")
        self.tools.config.app_ver.from_value("0.0.1")

        self.tools.config.from_yaml(APPLICATION_DEFAULT_CONFIG)
        self.tools.config.from_yaml(APPLICATION_CONFIG)
        if conect_url:
            self.tools.config.db.url.from_value(conect_url)

        self.tools.init_resources()

        self.db_helper = self.tools.db_helper()

    def execute(self, _config: Any, _task_data: Any) -> ConnectorProxyResponseDict:

        error = CommandErrorDict(
            message="У класса не обьявлен метод execute и вызвался default",
            error_code="sql_error"
        )

        result: ConnectorProxyResponseDict = {
            "command_response": None,
            "error": error,
            "command_response_version": 2,
            "spiff__logs": [],
        }

        return result
