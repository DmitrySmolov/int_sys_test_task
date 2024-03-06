from asyncio import (
    create_task, run, sleep, start_server, StreamReader, StreamWriter
)
from datetime import datetime
from os import path
import re

from config import (
    HOST, PORT, ENCODING, BUFFER_SIZE, client_constants as cl_const,
    server_constants as serv_const, logger_config as log_const
)
from utils import (
    decide_ignore_request, Serial, setup_logger, sleep_for_random_time,
)

module_name = path.basename(__file__).split('.')[0]
logger = setup_logger(module=module_name)

client_counter = 0

connected_clients = set()

server_serial = Serial()


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
    global client_counter
    global server_serial
    global connected_clients

    connected_clients.add(writer)
    client_counter += 1
    data = await reader.read(BUFFER_SIZE)
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
                client_counter=client_counter
            )
            writer.write(response_text.encode(ENCODING))
            await writer.drain()
            logger.info(
                log_const.SERVER_RES_TEMPLATE.format(
                    req_datetime=req_datetime.strftime(log_const.DATETIMEFMT),
                    req_text=reqest_text,
                    res_datetime=res_datetime.strftime(log_const.DATETIMEFMT),
                    res_text=response_text
                )
            )
        elif ignore:
            logger.info(
                log_const.SERVER_IGNORED_REQ_TEMPLATE.format(
                    req_datetime=req_datetime.strftime(log_const.DATETIMEFMT),
                    req_text=reqest_text
                )
            )


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
    create_task(send_keep_alive())

    server = await start_server(
        handle_client, HOST, PORT
    )
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    run(main())
