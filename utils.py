from asyncio import sleep
import logging
from os import makedirs, path
from random import randint

from config import logger_config


def setup_logger(module: str, number: int = None) -> logging.Logger:
    """
    Возвращает логгер для указанного модуля.

    Args:
        module (str): Название модуля. Либо 'server', либо 'client'.
        number (int, optional): Номер клиента. По умолчанию None.

    Returns:
        Logger: Логгер.
    """
    logger = logging.getLogger(
        module if module == 'server' else f'{module}{number}'
    )

    logger.setLevel(logging.INFO)

    file_path = (
        logger_config.SERVER_LOGFILE
        if module == 'server'
        else logger_config.CLIENT_LOGFILE.format(str(number))
    )
    file_dir = path.dirname(file_path)
    if not path.exists(file_dir):
        makedirs(file_dir)
    handler = logging.FileHandler(file_path, encoding='utf-8')
    logger.addHandler(handler)

    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    return logger


async def sleep_for_random_time(min_ms: int, max_ms: int) -> None:
    """
    Засыпает на время, выбранное случайным образом из заданного диапазона.

    Args:
        min_ms (int): Минимальное время в миллисекундах.
        max_ms (int): Максимальное время в миллисекундах.

    Returns:
        None
    """
    delay_ms = randint(min_ms, max_ms)
    delay_s = delay_ms / 1000
    await sleep(delay_s)


async def decide_ignore_request(chance_pct: int) -> bool:
    """
    Принимает решение случайным образом о том, игнорировать ли запрос  с
    учётом заданной вероятности.

    Args:
        chance_pct (int): Вероятность в процентах (от 0 до 100).

    Returns:
        bool: True, если запрос игнорируется, иначе False.
    """
    random_case = randint(1, 100)
    return random_case <= chance_pct


class Serial:
    """
    Класс для генерации порядкового номера.
    """
    def __init__(self, start: int = 0) -> None:
        """
        Инициализирует порядковый номер.

        Args:
            start (int, optional): Начальное значение порядкового номера.
                По умолчанию 0.

        Returns:
            None
        """
        self._serial = start

    def get(self) -> int:
        """
        Возвращает текущий порядковый номер и инкрементирует его.

        Returns:
            int: Текущий порядковый номер.
        """
        serial = self._serial
        self._serial += 1
        return serial
