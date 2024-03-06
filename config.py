from os import path

BASE_DIR = path.dirname(path.abspath(__file__))

HOST = '127.0.0.1'
PORT = 8888

ENCODING = 'ascii'
BUFFER_SIZE = 32

NUMBER_OF_CLIENTS = 2

SHUTDOWN_TIMELAPSE = 5 * 60


class ClientConstants:
    REQ_DELAY_INTERVAL_MS = (300, 3000)
    REQ_TEXT = 'PING'
    REQ_TEMPLATE = '[{serial}] {req_text}\n'
    REGEX_REQ_MSG = r'\[(?P<serial>\d+)\] (?P<req_text>\w+)'


class ServerConstants:
    REQ_IGNORE_CHANCE_PCT = 10
    RES_DELAY_INTERVAL_MS = (100, 1000)
    RES_TEXT = 'PONG'
    RES_TEMPLATE = (
        '[{server_serial}/{client_serial}] {res_text} ({client_counter})\n'
    )
    KA_INTERVAL_S = 5
    KA_TEXT = 'keepalive'
    KA_TEMPLATE = '[{serial}] {ka_text}\n'


class LoggerConfig:
    DATETIMEFMT = "%Y-%m-%d %H:%M:%S:%f"
    SERVER_RES_TEMPLATE = (
        '{req_datetime} - {req_text} - {res_datetime} - {res_text};'
    )
    SERVER_IGNORED_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - (проигнорировано);'
    )
    SERVER_LOGFILE = path.join(BASE_DIR, 'server', 'logs', 'server.log')
    CLIENT_RESPONDED_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - {res_datetime} - {res_text};'
    )
    CLIENT_TIMEOUT_REQ_TEMPLATE = (
        '{req_datetime} - {req_text} - {timeout_datetime} - (таймаут);'
    )
    CLIENT_KA_TEMPLATE = '{ka_datetime} - {ka_text};'
    CLIENT_LOGFILE = path.join(BASE_DIR, 'clients', 'logs', 'client{}.log')


client_constants = ClientConstants()
server_constants = ServerConstants()
logger_config = LoggerConfig()
