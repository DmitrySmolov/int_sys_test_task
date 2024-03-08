from asyncio import (
    wait_for, open_connection, run, sleep, StreamReader, StreamWriter,
    TimeoutError, create_task
)
from collections import deque
from datetime import datetime
import re

from config import (
    client_constants as cl_const, logger_config as log_const, HOST, PORT,
    ENCODING, RESPONSE_TIMEOUT,
    server_constants as serv_const, SHUTDOWN_TIMELAPSE
)
from utils import (
    get_module_name, parse_module_number, RespondedRequest, Serial,
    setup_logger, sleep_for_random_time
)

module_name = get_module_name(__file__)
client_number = parse_module_number()
logger = setup_logger(module=module_name, number=client_number)

client_serial = Serial()

responded_requests = deque()


async def client_writer(writer: StreamWriter) -> None:
    """
    Отправляет запросы на сервер с определённой периодичностью и проверяет
    ответ в очереди responded_requests.

    Args:
        writer (StreamWriter): объект StreamWriter.

    Returns:
        None
    """

    global client_serial
    global responded_requests

    while True:
        await sleep_for_random_time(*cl_const.REQ_DELAY_INTERVAL_MS)
        serial = client_serial.get()
        request_text = cl_const.REQ_TEMPLATE.format(
            serial=serial, req_text=cl_const.REQ_TEXT
        )
        writer.write(request_text.encode(ENCODING))
        await writer.drain()
        request_datetime = datetime.now()
        create_task(_handle_response(serial, request_datetime, request_text))


async def client_reader(reader: StreamReader) -> None:
    """
    Получает ответы от сервера и проверяет их на соответствие шаблону.
    Если ответ соответствует шаблону, добавляет его в очередь
    responded_requests. Если ответ - keep-alive, то делает соответствующую
    запись в лог.

    Args:
        reader (StreamReader): объект StreamReader.

    Returns:
        None
    """
    global responded_requests

    while True:
        data = await reader.readline()
        if data:
            response_text = data.decode(ENCODING)
            match = re.match(serv_const.REGEX_RES_MSG, response_text)
            if match:
                client_serial = int(match.group('client_serial'))
                res_datetime = datetime.now()
                responded_requests.append(
                    RespondedRequest(
                        client_serial=client_serial,
                        res_text=response_text,
                        res_datetime=res_datetime,
                    )
                )
                continue
            match = re.match(serv_const.REGEX_KA_MSG, response_text)
            if match:
                ka_datetime = datetime.now()
                ka_text = response_text
                logger.info(
                    log_const.CLIENT_KA_TEMPLATE.format(
                        ka_datetime=ka_datetime.strftime(
                            log_const.DATETIMEFMT
                        ),
                        ka_text=ka_text
                    )
                )


async def main() -> None:
    """
    Основная функция, создающая соединение с сервером и запускающая
    корутины client_writer и client_reader.

    Returns:
        None
    """
    try:
        reader, writer = await open_connection(HOST, PORT)
        print(f'Connected to {HOST}:{PORT}')
        writer_task = create_task(client_writer(writer))
        reader_task = create_task(client_reader(reader))
        await sleep(SHUTDOWN_TIMELAPSE)
        await _safe_shutdown(writer_task, writer, reader_task)

    except KeyboardInterrupt:
        await _safe_shutdown(writer_task, writer, reader_task)


async def _check_responded_request(serial: int) -> RespondedRequest:
    """
    Проверяет наличие ответа сервера в очереди responded_requests по
    порядковому номеру запроса.

    Args:
        serial (int): порядковый номер запроса.

    Returns:
        RespondedRequest: объект класса RespondedRequest.
    """
    while True:
        if (
            responded_requests
            and responded_requests[0].client_serial == serial
        ):
            return responded_requests.popleft()
        await sleep(0.1)


async def _handle_response(
    serial: int, request_datetime: datetime, request_text: str
) -> None:
    """
    Проверяет наличие ответа сервера в очереди responded_requests по
    порядковому номеру запроса. Если ответ есть, делает соответствующую
    запись в лог. Если ответа нет, делает запись в лог об отсутствии ответа.

    Args:
        serial (int): порядковый номер запроса.
        request_datetime (datetime): время отправки запроса.
        request_text (str): текст запроса.

    Returns:
        None
    """
    try:
        responded_request = await wait_for(
            _check_responded_request(serial), timeout=RESPONSE_TIMEOUT
        )
        responded_request.req_datetime = request_datetime
        responded_request.req_text = request_text
        logger.info(
            responded_request.to_log()
        )
    except TimeoutError:
        timeout_datetime = datetime.now()
        logger.info(
            log_const.CLIENT_TIMEOUT_REQ_TEMPLATE.format(
                req_datetime=request_datetime.strftime(
                    log_const.DATETIMEFMT
                ),
                req_text=request_text,
                timeout_datetime=timeout_datetime.strftime(
                    log_const.DATETIMEFMT
                )
            )
        )


async def _safe_shutdown(writer_task, writer, reader_task) -> None:
    """
    Безопасно закрывает соединение с сервером.

    Args:
        reader (StreamReader): объект StreamReader.
        writer (StreamWriter): объект StreamWriter.

    Returns:
        None
    """
    writer_task.cancel()
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    reader_task.cancel()


if __name__ == '__main__':
    run(main())
