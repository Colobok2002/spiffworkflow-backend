from celery import shared_task


@shared_task
def add_message_to_queue(message: str) -> str:
    # Пример добавления сообщения в очередь
    print(f"Сообщение добавлено в очередь: {message}")
    return message


@shared_task
def process_message_from_queue(message: str) -> None:
    # Пример обработки сообщения из очереди
    print(f"Обработка сообщения из очереди: {message}")
