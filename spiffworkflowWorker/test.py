from spiffworkflowWorker.spiffManager import SpiffworkflowWorkerManager
from spiffworkflowWorker.di.celery import CeleryDI
from spiffworkflowWorker.di import APPLICATION_CONFIG, APPLICATION_DEFAULT_CONFIG

if __name__ == "__main__":

    demosignal_swm = SpiffworkflowWorkerManager(
        process_name="test:demosignal",
        modified_message_name="init_message"
    )

    test233 = SpiffworkflowWorkerManager(
        process_name="test:test233",
    )

    celeryDI = CeleryDI()

    di = CeleryDI()
    di.config.from_yaml(APPLICATION_DEFAULT_CONFIG)
    di.config.from_yaml(APPLICATION_CONFIG)

    di.init_resources()
    logger = di.common_di().logger()

    tasks = di.tasks()

    tasks.clear_queues()

    tasks.enqueue_start_task(demosignal_swm)

    tasks.enqueue_start_task(test233)
