from asyncio import run, start_server, StreamReader, StreamWriter
from os import path

from config import HOST, PORT, ENCODING, BUFFER_SIZE
from utils import (
    decide_ignore_request, Serial, setup_logger, sleep_for_random_time,
)

module_name = path.basename(__file__).split('.')[0]
logger = setup_logger(module=module_name)


async def handle_client(
    reader: StreamReader, writer: StreamWriter
) -> None:
    """
    Обработчик клиента.

    Args:
        reader (StreamReader): Объект чтения.
        writer (StreamWriter): Объект записи.

    Returns:
        None
    """
    pass
