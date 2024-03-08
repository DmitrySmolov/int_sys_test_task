# Тестовое задание для "Интеллектуальные Системы"

В данном проекте запускается сервер и два клиента в разных процессах. В течение 5 минут клиенты и сервер обмениваются условными ASCII-сообщениями через TCP-соединение. Проект выполнен в качестве тестового задания.

## Технологии

- Python 3.10
- Asyncio

## Файловая структура

```
.
├── clients
│   ├── logs
│   │   ├── .gitkeep
│   │   ├── client1.log
│   │   └── client2.log
│   ├── __init__.py
│   └── client.py
├── server
│   ├── logs
│   │   ├── .gitkeep
│   │   └── server.log
│   ├── __init__.py
│   └── server.py
├── .gitignore
├── config.py
├── LICENSE
├── README.md
├── run_server_and_clients.sh
└── utils.py
```

## Конфигурации

Все ключевые конфигурации сервера, клиента, логгера, включая форматы отправляемых сообщений и записей в лог выставлены в файле `config.py`.

## Запуск приложения

Можно запустить сервер и два клиента, выполнив следующий скрипт в терминале, назодясь в корне репозитория:

```
chmod +x run_server_and_clients.sh && ./run_server_and_clients.sh
```
Либо открыть терминал для сервера и запустить его:
```
python -m server.server
```
а также открыть нужное количество терминалов для клиентов и запустить их с указанием номера клиента в качестве аргумента:
```
python -m clients.client <номер клиента, например 1>
```
## Расположение логов

Логи расположены директориях `clients/logs/` - для клиентов и `server/logs` - для сервера. Согласно условию задания, логи, сформированные в ходе 5-минутной работы, уже присутствуют.

Благодарю за внимание! :pray:
