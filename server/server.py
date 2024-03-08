from asyncio import (
    run, sleep, start_server, StreamReader, StreamWriter, create_task,
)
from datetime import datetime
import re

from config import (
    HOST, PORT, ENCODING, client_constants as cl_const,
    server_constants as serv_const, logger_config as log_const,
    SHUTDOWN_TIMELAPSE
)
from utils import (
    decide_ignore_request, get_module_name, Serial, setup_logger,
    sleep_for_random_time,
)

module_name = get_module_name(__file__)
logger = setup_logger(module=module_name)

client_counter = 0

connected_clients = set()

server_serial = Serial()


async def handle_client(
    reader: StreamReader, writer: StreamWriter, client_id: int
) -> None:
    """
    Обработчик клиента.

    Args:
        reader (StreamReader): Объект чтения.
        writer (StreamWriter): Объект записи.
        client_id (int): Идентификатор клиента.

    Returns:
        None
    """
    global server_serial
    global connected_clients

    connected_clients.add(writer)

    while True:
        data = await reader.readline()
        if data:
            req_datetime = datetime.now()
            reqest_text = data.decode(ENCODING)
            ignore = decide_ignore_request(
                chance_pct=serv_const.REQ_IGNORE_CHANCE_PCT
            )
            if not ignore:
                match = re.match(cl_const.REGEX_REQ_MSG, reqest_text)
                client_serial = match.group('serial') if match else 'N/A'
                res_text = serv_const.RES_TEXT
                await sleep_for_random_time(*serv_const.RES_DELAY_INTERVAL_MS)
                res_datetime = datetime.now()
                response_text = serv_const.RES_TEMPLATE.format(
                    server_serial=server_serial.get(),
                    client_serial=client_serial,
                    res_text=res_text,
                    client_id=client_id
                )
                writer.write(response_text.encode(ENCODING))
                await writer.drain()
                logger.info(
                    log_const.SERVER_RES_TEMPLATE.format(
                        req_datetime=req_datetime.strftime(
                            log_const.DATETIMEFMT
                        ),
                        req_text=reqest_text,
                        res_datetime=res_datetime.strftime(
                            log_const.DATETIMEFMT
                        ),
                        res_text=response_text
                    )
                )
            elif ignore:
                logger.info(
                    log_const.SERVER_IGNORED_REQ_TEMPLATE.format(
                        req_datetime=req_datetime.strftime(
                            log_const.DATETIMEFMT
                        ),
                        req_text=reqest_text
                    )
                )
        else:
            connected_clients.remove(writer)
            writer.close()
            await writer.wait_closed()
            break


async def handle_client_wrapper(
    reader: StreamReader, writer: StreamWriter
) -> None:
    """
    Обертка обработчика клиента для получения идентификатора клиента.

    Args:
        reader (StreamReader): Объект чтения.
        writer (StreamWriter): Объект записи.

    Returns:
        None
    """
    global client_counter

    client_counter += 1
    await handle_client(reader, writer, client_counter)


async def send_keep_alive() -> None:
    """
    Отправка keep-alive сообщений с заданным интервалом.

    Returns:
        None
    """
    global server_serial
    global connected_clients

    while True:
        await sleep(serv_const.KA_INTERVAL_S)
        addrs = []
        for writer in connected_clients:
            addr = writer.get_extra_info('peername')
            addrs.append(addr)
        if not connected_clients:
            continue
        for writer in connected_clients:
            keep_alive = serv_const.KA_TEMPLATE.format(
                serial=server_serial.get(),
                ka_text=serv_const.KA_TEXT
            )
            writer.write(keep_alive.encode(ENCODING))
            await writer.drain()


async def main() -> None:
    """
    Основная функция.

    Returns:
        None
    """
    try:
        keep_alive_task = create_task(send_keep_alive())
        server = await start_server(
            handle_client_wrapper, HOST, PORT
        )
        await sleep(SHUTDOWN_TIMELAPSE)
        await _safe_shutdown(keep_alive_task, server)

    except KeyboardInterrupt:
        await _safe_shutdown(keep_alive_task, server)


async def _safe_shutdown(keep_alive_task, server) -> None:
    """
    Остановка сервера.

    Args:
        keep_alive_task: Задача отправки keep-alive сообщений.
        server: Сервер.

    Returns:
        None
    """
    keep_alive_task.cancel()
    server.close()
    await server.wait_closed()
    if connected_clients:
        for writer in connected_clients:
            writer.close()
            await writer.wait_closed()


if __name__ == '__main__':
    run(main())
