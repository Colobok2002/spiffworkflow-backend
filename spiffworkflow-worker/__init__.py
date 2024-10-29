'''
:mod:`__init__` -- Класс для работы с method
===================================
.. moduleauthor:: ilya Barinov (i-barinov@it-serv.ru)
'''

from uuid import UUID
import json
import re
from typing import Any, Dict
from pydantic import BaseModel
import requests


class RequestMethods:
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"
    patch = "patch"


class Process(BaseModel):
    id: int = None


class Task(BaseModel):
    id: UUID = None
    process: Process = None


class RequestHelper:
    """Клас по отправки запросов"""

    def __init__(self, api):
        self.api = api
        self.headers = {}

    def set_api_url(self, url: str) -> None:
        """Позволяет изменять API url"""
        self.api = url

    def set_authorization_token(self, token: str) -> None:
        """Позволяет изменять Auth token"""
        self.headers['authorization'] = token

    def _request(self, rout: str, method: str = RequestMethods.get, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Выполнение запроса

        :param rout: Url эндпоинта
        :param method: Метод вызыва из класса RequestMethods, defaults to RequestMethods.get
        :param params: Словарь парраметров для запроса, defaults to None
        """
        request_method = getattr(requests, method)

        if 'headers' in kwargs:
            kwargs['headers'].update(self.headers)
        else:
            kwargs['headers'] = self.headers

        if method == RequestMethods.get:
            response: requests.Response = request_method(self.api + rout, params=params, **kwargs)
        else:
            response: requests.Response = request_method(self.api + rout, json=params, **kwargs)

        return response

    def get_json(self, rout, method=RequestMethods.get, **kwargs) -> dict:
        """Получение json из запроса

        :param rout: Url эндпоинта
        :param method: Метод вызыва из класса RequestMethods, defaults to RequestMethods.get
        :param kwargs: Дополнительные параметры запроса
        """

        rData = self._request(rout=rout, method=method, **kwargs)
        if 200 <= rData.status_code < 300:
            clean_text = re.search(r'{.*}', rData.text, flags=re.DOTALL).group(0)
            result = json.loads(clean_text)
            return result
        else:
            raise Exception(f'Request failed with status code {rData.status_code}')


class SpiffworkflowWorker:
    """Наборо функций для взаимодействия с процессом"""

    def __init__(self):
        self.api = 'http://localhost:8000/v1.0/'
        self.rh = RequestHelper(self.api)
        self.init_token_auth()
        pass

    def init_token_auth(self):
        """Инициализация токена авторизации"""
        token = self.get_token()

        if token.get("access_token", None) is None:
            raise Exception(f'Access token undefaind')

        self.rh.set_authorization_token(token.get("access_token", None))

    def get_token(self) -> dict:
        """Получить новый токен"""
        self.rh.set_api_url("http://localhost:8000/openid/")

        kwargs = {
            "headers": {
                "Authorization": "Basic c3BpZmZ3b3JrZmxvdy1iYWNrZW5kOkpYZVFFeG0wSmhRUEx1bWdIdElJcWY1MmJEYWxIejBx"
            }
        }

        rData = self.rh.get_json(
            rout="token?code=admin:test", method=RequestMethods.post, **kwargs)

        self.rh.set_api_url(self.api)

        return rData

    def get_process_models(self):
        """Получить все доступные процессы для запускаА
        """
        rout = "process-models"
        params = {
            "per_page": 1000,
            "recursive": True,
            "include_parent_groups": True
        }

        rData = self.rh.get_json(rout=rout, params=params).get("results", None)

        return rData


class SpiffworkflowWorkerManager:
    """Менелдер для работы с конкретным процессом
    """

    def __init__(self, process_name: str):
        self.process_name = process_name
        self.sw = SpiffworkflowWorker()

    def start(self):
        """Запус процесса

        :return: _description_
        :rtype: _type_
        """
        # Инициализируем процесс
        rout = f"process-instances/{self.process_name}"
        rData = self.sw.rh.get_json(rout=rout, method=RequestMethods.post)

        proc = Process()
        proc.id = rData.get("id", None)
        # # {"id": 189, "process_model_identifier": "test/test233", "process_model_display_name": "test233", "process_initiator_id": 1, "start_in_seconds": 1730200470,
        # #     "end_in_seconds": None, "updated_at_in_seconds": 1730200470, "created_at_in_seconds": 1730200470, "status": "not_started", "bpmn_version_control_identifier": None}

        # Зускаем его
        rout = f"process-instances/{self.process_name}/{proc.id}/run"
        rData = self.sw.rh.get_json(rout=rout, method=RequestMethods.post)
        # {"id": 189, "status": "user_input_required", "process_model_identifier": "test/test233",
        #     "process_model_display_name": "test233", "updated_at_in_seconds": 1730200472, "process_model_uses_queued_execution": false}

        # Получаем информации по получивщейся задачи
        rout = f"tasks/{proc.id}?execute_tasks=true"
        rData = self.sw.rh.get_json(rout=rout)
        task = Task()
        task.id = rData.get("task", {}).get("id", None)
        task.process = proc

        # {
        #     "type": "task",
        #     "task": {
        #         "id": "1746dc07-1241-4746-a492-d43789a30d7d",
        #         "name": "Activity_19exf2m",
        #         "title": null,
        #         "type": "Manual Task",
        #         "state": "READY",
        #         "lane": null,
        #         "can_complete": true,
        #         "form": null,
        #         "documentation": "",
        #         "data": {},
        #         "multi_instance_type": null,
        #         "multi_instance_count": "",
        #         "multi_instance_index": "",
        #         "process_identifier": "Process_test233_9knu6a0",
        #         "properties": {
        #             "instructionsForEndUser": "**scalar** \n\n\n```json\n{\"body\": {\"sql_result\": \"chk\"}, \"mimetype\": \"application/json\", \"operator_identifier\": \"sql/SqlScalar\"}\n```\n\n\n**all** \n\n```json\n{\"body\": {\"sql_result\": [[\"chk\", \"sd_close_periods\", 1, null, null, null], [\"chk\", \"sd_message_log\", 1, null, null, null], [\"chk\", \"ss_message_categories\", 2, null, null, null], [\"chk\", \"ss_message_types\", 2, null, null, null], [\"chk\", \"ss_sections\", 2, null, null, null], [\"chk\", \"ss_types_categories\", 2, null, null, null], [\"dbo\", \"cd_access_list_890\", 1, null, null, null], [\"dbo\", \"cd_advance_payments\", 1, null, null, null], [\"dbo\", \"cd_executives\", 1, null, null, null], [\"dbo\", \"cd_normativ_on_heating\", 1, null, null, null]]}, \"mimetype\": \"application/json\", \"operator_identifier\": \"sql/SqlAllNew\"}\n```"
        #         },
        #         "process_instance_id": 190,
        #         "process_instance_status": null,
        #         "process_model_display_name": "test233",
        #         "process_group_identifier": null,
        #         "process_model_identifier": "test/test233",
        #         "bpmn_process_identifier": null,
        #         "form_schema": null,
        #         "form_ui_schema": null,
        #         "parent": "0ff98a0d-dd33-4ce5-a02c-9f7d06ffa5bb",
        #         "event_definition": null,
        #         "error_message": null,
        #         "assigned_user_group_identifier": null,
        #         "potential_owner_usernames": null,
        #         "process_model_uses_queued_execution": null
        #     }
        # }

        # Закидыввам сообщение иниализации
        rout = f"messages/init_message?modified_message_name=init_message"
        params = {
            "data": "Hello world"
        }
        rData = self.sw.rh.get_json(rout=rout, method=RequestMethods.post, params=params)

        return rData


if __name__ == "__main__":
    sw = SpiffworkflowWorkerManager(
        process_name="test:demosignal"
    )
    sw.start()
