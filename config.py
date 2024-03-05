from os import path

BASE_DIR = path.dirname(path.abspath(__file__))

HOST = '127.0.0.1'
PORT = 8888

ENCODING = 'ascii'
BUFFER_SIZE = 32

NUMBER_OF_CLIENTS = 2

SHUTDOWN_TIMELAPSE = 5 * 60


class Client:
    REQ_DELAY_INTERVAL_S = (0.3, 3)
    REQ_TEXT = 'PING'
    REQ_TEMPLATE = '[{serial}] {message_text}\n'


class Server:
    REQ_IGNORE_RATE = 0.1
    RESP_DELAY_INTERVAL_S = (0.1, 1)
    RESP_TEXT = 'PONG'
    RESP_TEMPLATE = (
        '[{serial}/{client_req_serial}] {resp_text} ({client_id})\n'
    )
    KA_INTERVAL_S = 5
    KA_TEXT = 'keepalive'
    KA_TEMPLATE = '[{serial}] {ka_text}\n'


class Logger:
    DATETIMEFMT = "%Y-%m-%d T %H:%M:%S:%f"
    SERVER_RESP_TEMPLATE = (
        '{req_datetime} - {req_text} - {resp_datetime} - {resp_text}'
    )
    SERVER_IGNORED_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - (проигнорировано)'
    )
    SERVER_LOGFILE = path.join(BASE_DIR, 'server', 'logs', 'server.log')
    CLIENT_RESPONDED_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - {resp_datetime} - {resp_text}'
    )
    CLIENT_TIMEOUT_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - {timeout_datetime} - (таймаут)'
    )
    CLIENT_KA_TEMPLATE = '{ka_datetime} - {ka_text}'
    CLIENT_LOGFILE = path.join(BASE_DIR, 'clients', 'logs', 'client{}.log')
