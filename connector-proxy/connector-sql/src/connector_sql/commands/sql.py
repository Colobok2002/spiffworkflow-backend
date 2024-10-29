'''
:mod:`sql` -- Коннекторы для работы с bd
===================================
.. moduleauthor:: ilya Barinov (i-barinov@it-serv.ru)
'''

from typing import Any

from connector_sql import SqlConnector
from spiffworkflow_connector_command.command_interface import CommandErrorDict
from spiffworkflow_connector_command.command_interface import CommandResponseDict
from spiffworkflow_connector_command.command_interface import ConnectorCommand
from spiffworkflow_connector_command.command_interface import ConnectorProxyResponseDict

from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class SqlScalar(SqlConnector):

    def execute(self, _config: Any, _task_data: Any) -> ConnectorProxyResponseDict:
        error: CommandErrorDict | None = None
        result = None
        try:
            with self.db_helper.sessionmanager() as session:
                session: Session = session
                result = session.execute(text(self.sql_query)).fetchone()
                result = result[0] if result else None
        except Exception as e:
            result = None
            error = CommandErrorDict(
                message=str(e),
                error_code="sql_error"
            )

        return_response: CommandResponseDict = {
            "body": {
                "sql_result": result,
            },
            "mimetype": "application/json",
        }

        result: ConnectorProxyResponseDict = {
            "command_response": return_response,
            "error": error,
            "command_response_version": 2,
            "spiff__logs": [],
        }

        return result


class SqlAllNew(SqlConnector):

    def __init__(self, sql_query: str = None, conect_url: str | None = None, page: str | None = None, size: str | None = None):
        super().__init__(sql_query=sql_query, conect_url=conect_url)

        self.page = page
        self.size = size

    def execute(self, _config: Any, _task_data: Any) -> dict:
        error: CommandErrorDict | None = None
        result = None
        try:
            with self.db_helper.sessionmanager() as session:
                session: Session = session

                if not self.page is None and not self.size is None:
                    offset = (self.page - 1) * self.size
                    limit = self.size
                    clean_query = self.sql_query.rstrip(";")

                    paginated_query = f"{clean_query} LIMIT :limit OFFSET :offset"
                    result_query = session.execute(text(paginated_query), {"limit": limit, "offset": offset}).all()
                else:
                    result_query = session.execute(text(self.sql_query)).all()

                result = [tuple(row) for row in result_query]

        except Exception as e:
            result = None
            error = CommandErrorDict(
                message=str(e),
                error_code="sql_error"
            )

        return_response: CommandResponseDict = {
            "body": {
                "sql_result": result,
            },
            "mimetype": "application/json",
        }

        result: ConnectorProxyResponseDict = {
            "command_response": return_response,
            "error": error,
            "command_response_version": 2,
            "spiff__logs": [],
        }

        return result
