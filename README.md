# Запуск проекта

1) Такой код чтоб добавить все необходимые переменный окружения

```
export FLASK_DEBUG=0
export FLASK_SESSION_SECRET_KEY=${FLASK_SESSION_SECRET_KEY:-e7711a3ba96c46c68e084a86952de16f}
export SPIFFWORKFLOW_BACKEND_BPMN_SPEC_ABSOLUTE_DIR="./process_models"
export SPIFFWORKFLOW_BACKEND_DATABASE_URI="mysql+mysqldb://root:${SPIFFWORKFLOW_BACKEND_MYSQL_ROOT_DATABASE:-my-secret-pw}@127.0.0.1:3306/${SPIFFWORKFLOW_BACKEND_DATABASE_NAME:-spiffworkflow_backend_development}"
export SPIFFWORKFLOW_BACKEND_ENV=${SPIFFWORKFLOW_BACKEND_ENV:-local_development}
export SPIFFWORKFLOW_BACKEND_LOAD_FIXTURE_DATA=${SPIFFWORKFLOW_BACKEND_LOAD_FIXTURE_DATA:-false}
export SPIFFWORKFLOW_BACKEND_OPEN_ID_SERVER_URL=${SPIFFWORKFLOW_BACKEND_OPEN_ID_SERVER_URL:-http://localhost:8000/realms/spiffworkflow-local}
export SPIFFWORKFLOW_BACKEND_PERMISSIONS_FILE_NAME="local_development.yml"
export SPIFFWORKFLOW_BACKEND_PORT=8000
export SPIFFWORKFLOW_BACKEND_RUN_BACKGROUND_SCHEDULER_IN_CREATE_APP="false"
export SPIFFWORKFLOW_BACKEND_URL_FOR_FRONTEND=${SPIFFWORKFLOW_BACKEND_URL_FOR_FRONTEND:-http://localhost:7001}
export SPIFFWORKFLOW_BACKEND_UPGRADE_DB=true
export SPIFFWORKFLOW_BACKEND_URL="http://localhost:8000"
export SPIFFWORKFLOW_BACKEND_LOG_LEVEL="debug"
export SPIFFWORKFLOW_BACKEND_GIT_PUBLISH_CLONE_URL="https://github.com/sartography/sample-process-models.git"
export SPIFFWORKFLOW_BACKEND_GIT_USERNAME="sartography-automated-committer"
export SPIFFWORKFLOW_BACKEND_GIT_USER_EMAIL="sartography-automated-committer@users.noreply.github.com"
export SPIFFWORKFLOW_BACKEND_EXTENSIONS_API_ENABLED="true"
export SPIFFWORKFLOW_BACKEND_GIT_SOURCE_BRANCH="sample-models-1"
```

2. Запускаем dev.docker-compose.yml для поднятия базы mysql
3. Запускаем скрипт ./bin/run_server_locally для поднятия основнова сервера
4. Для поднятия микро сервиса по servise task

   ```
   cd onnector-proxy
   ./bin/run_server_locally
   ```

Если все прошло успешно сервис должен был подгяться на 8000 порту

# Создание connector-proxy

Для добалвения нового сервсиса переходим в папку connector-proxy

В ней лежит папка connector-example ( это пример того как должен выглядеть proxy ) копируем и и переименувываем ( важно чтоб название начинало connector-* )

Для примера я назвал **connector-sql**

Для завершении регистрации  в поле в **pyproject.toml** мы должны прописать

```
connector-sql = {path = "./connector-sql" }
```

После этого ваш коннектор станет доступен в web версии


# Описание

## connector-proxy

Сервис для создания собственных коннтеров 


## spiffworkflow-worker

Сервис для запуска задачь из кода python


## spiffworkflow

В папке src ледит основной bac-end 


# Dockers

dev.docker-compose.yml - поднимается фронт и база для локальной разработки

Prod.docker-compose copy.yml -поднимается все необходимое из локальный файлов

Ofichial.docker-compose.yml - поднимается все из готовый образов
