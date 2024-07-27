# Основные отличия протоколов uWSGI и HTTP

## Причины разработки протокола uWSGI

 - **Упрощение управления бинарными данными**:
   - Управление бинарными данными проще и дешевле, чем парсинг строк: http является cтроковым протоколом, более хьюмн-ридбл. В то время как uwsgi - бинарный (смотерть риализацию в скрипте)
 - **Повышение производительности**:
   - Парсинг HTTP-запросов является медленным процессом.
 - **Избежание повторного выполнения сложных задач**:
   - Веб-сервер уже парсит HTTP-запрос, нет смысла делать это дважды.
 - **Простота парсинга для машины**:
   - Протокол uWSGI очень прост для машинного парсинга, в отличие от HTTP.

HTTP в основном используется для связи между клиентом и веб-сервером, в то время как протокол uwsgi предназначен для общения между приложением и веб сервером, как и другие протоколы типа scgi, fscgi 

## Структура запросов

### HTTP-запрос

 ```
 GET /index.html HTTP/1.1
 Host: example.com
 User-Agent: curl/7.68.0
 Accept: */*
 ```

### uWSGI-запрос

 ```
 [4 bytes header] [payload]
 ```

## Заключение

 Протокол uWSGI был разработан для увеличения производительности веб-приложений, минимизации накладных расходов на парсинг запросов и упрощения обработки данных на сервере. Это особенно важно для высоконагруженных систем, где каждая единица вычислительных ресурсов имеет значение. Протокол uWSGI является более эффективным для внутреннего взаимодействия между веб-серверами и приложениями, что делает его предпочтительным выбором для многих высокопроизводительных веб-приложений.


## СКРИПТЫ
В данной директории лежат

foobar.py - простое uwsgi приложение

myflaskapp.py - простое приложение на flask запускаемое uwsgi

uwsgi_client.py - реализация клиента uwsgi на python. Запуск: `python3 uwsgi_client.py`. Для работы также необходимо настроить минимальный конфиг в nginx со следующим конфигом в любом локейшене

```
uwsgi_pass unix:///tmp/uwsgi.sock;
include uwsgi_params;
```

И обращаться к скрипту через nginx. Примеры выводов:

```
uWSGI server listening on 0.0.0.0:4040
Connection from ('127.0.0.1', 48932)
Header: b'\x00I\x01\x00'
Received var block size: 329
Raw var_block content: b'\x0c\x00QUERY_STRING\x00\x00\x0e\x00REQUEST_METHOD\x03\x00GET\x0c\x00CONTENT_TYPE\x00\x00\x0e\x00CONTENT_LENGTH\x00\x00\x0b\x00REQUEST_URI\x02\x00/u\t\x00PATH_INFO\x02\x00/u\r\x00DOCUMENT_ROOT\r\x00/var/www/html\x0f\x00SERVER_PROTOCOL\x08\x00HTTP/1.1\x0e\x00REQUEST_SCHEME\x04\x00http\x0b\x00REMOTE_ADDR\t\x00127.0.0.1\x0b\x00REMOTE_PORT\x05\x0055986\x0b\x00SERVER_PORT\x02\x0080\x0b\x00SERVER_NAME\x01\x00_\t\x00HTTP_HOST\t\x00127.0.0.1\x0f\x00HTTP_USER_AGENT\x0b\x00curl/7.81.0\x0b\x00HTTP_ACCEPT\x03\x00*/*'
Len of var_block content: 329
Environment variables:
QUERY_STRING:
REQUEST_METHOD: GET
CONTENT_TYPE:
CONTENT_LENGTH:
REQUEST_URI: /u
PATH_INFO: /u
DOCUMENT_ROOT: /var/www/html
SERVER_PROTOCOL: HTTP/1.1
REQUEST_SCHEME: http
REMOTE_ADDR: 127.0.0.1
REMOTE_PORT: 55986
SERVER_PORT: 80
SERVER_NAME: _
HTTP_HOST: 127.0.0.1
HTTP_USER_AGENT: curl/7.81.0
HTTP_ACCEPT: */*
Request body:
```

## Ссылкi
uwsgi source repo - https://github.com/unbit/uwsgi/tree/master
uwsgi docs - https://uwsgi-docs.readthedocs.io/en/latest/index.html
uwsgi FAQ - https://uwsgi-docs.readthedocs.io/en/latest/FAQ.html

## Что такое этот ваш uWSGI
Важно понимать, что есть uWSGI, а есть uwsgi
uwsgi - протокол передачи запросов от веб-сервера к приложению
uWSGI - сервер приложения, который менеджет коннекшены, запросы и прочее

В uwsgi - по факту полноценный веб сервер (поддержку проксирования не чекал). Можно сравнить с spawn-fcgi бинарником, там правда функционал минимальный - создание форков приложения и все.
А вот uWSGI Поддерживает слудующие функции
* кучу протоколов типа http, https
* разные ЯП
* управление процессами: треды и форки
* конфигурация через файлы
* отдачу статических файлов тоже вроде поддерживает
* логи
* масштабирование 
* и еще какие то фишки

Вобщем выполняет функции обычного веб-сервера. Но не такой жесткий и надежный как nginx и проч.

Можно позапускать примеры из этой директории (https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)
```
# запуск с протоколом uwsgi
uwsgi --socket 127.0.0.1:3031 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191
# запуск с прокси
uwsgi --http :9090 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191
# запуск с http протоколом
uwsgi --http-socket 127.0.0.1:3031 --wsgi-file foobar.py --master --processes 4 --threads 2 --stats 127.0.0.1:9191

# flask
uwsgi --socket 127.0.0.1:3031 --wsgi-file myflaskapp.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191
```
