# README

## Введение

SCGI (Simple Common Gateway Interface) — это протокол, который определяет формат передачи данных между веб-сервером и сервером приложения. Этот протокол используется для того, чтобы веб-сервер мог передавать HTTP-запросы вашему приложению, а затем получать ответы от него. Важно понимать, что SCGI определяет только формат передачи данных и не влияет на то, как именно эти данные обрабатываются внутри вашего приложения.

## Основные концепции SCGI

### Пример работы SCGI

Когда веб-сервер получает HTTP-запрос от клиента, он преобразует этот запрос в формат SCGI и отправляет его на сервер приложения. Формат SCGI использует netstring для передачи данных. Netstring имеет следующий формат: `[len]":"[string]","`, где `[len]` — длина строки, а `[string]` — сама строка.

#### Пример запроса в формате SCGI

```
327:CONTENT_LENGTH0REQUEST_METHODGETREQUEST_URI/scgi?test=aQUERY_STRINGtest=aCONTENT_TYPEDOCUMENT_URI/scgiDOCUMENT_ROOT/var/www/htmlSCGI1SERVER_PROTOCOLHTTP/1.1REQUEST_SCHEMEhttpREMOTE_ADDR127.0.0.1REMOTE_PORT60212SERVER_PORT80SERVER_NAME_HTTP_HOST127.0.0.1HTTP_USER_AGENTcurl/7.81.0HTTP_ACCEPT*/*,
```

### Обработка SCGI-запроса

Для обработки SCGI-запроса на сервере приложения необходимо выполнить следующие шаги:

1. Получить данные из сокета:

```python
data = client_socket.recv(4096)
```

2. Распарсить данные, чтобы извлечь заголовки и тело запроса:

```python
header_size_str, rest = data.split(b':', 1)
header_size = int(header_size_str)
headers_data, body = rest[:header_size], rest[header_size+1:]
```

3. Преобразовать заголовки в словарь для удобного использования:

```python
def parse_scgi_headers(headers_data):
    headers = {}
    parts = headers_data.split('\x00')
    for i in range(0, len(parts) - 1, 2):
        headers[parts[i]] = parts[i + 1]
    return headers
```

## Первая версия CGI

Первая версия CGI (Common Gateway Interface) не была полноценным протоколом. Она просто форкала процесс воркера Apache с переменными окружения. Это можно назвать протоколом, поскольку для реализации требовалась библиотека, которая принимала запрос и выполняла необходимые действия для его обработки и формирования ответа.

## FastCGI и SCGI

FastCGI и SCGI — это конкретные протоколы, которые определяют формат передачи запросов от веб-сервера к скрипту. В SCGI формат передачи данных — это netstring. Пример формата netstring:

```
[len]":"[string]", 
```

где `[len]` — длина строки, а `[string]` — сама строка.

### Как это происходит

1. Клиент отправляет HTTP GET запрос.
2. Веб-сервер преобразует этот запрос в формат SCGI.
3. Веб-сервер отправляет преобразованный запрос на SCGI сервер.
4. На сервере приложения библиотека парсит запрос в формате SCGI.

Чтобы написать клиент на любом языке программирования для SCGI протокола, нужно просто распарсить данные в этом формате.

> 2 пункт Не проверялся

### Пример функций для парсинга SCGI запроса

```python
class SCGIHandler:
    def __init__(self, conn):
        self.conn = conn

    def handle(self):
        data = self.conn.recv(4096)
        headers, body = self.parse_scgi_request(data)
        self.produce(headers, body)

    def parse_scgi_request(self, data):
        header_size_str, rest = data.split(b':', 1)
        header_size = int(header_size_str)
        headers_data, body = rest[:header_size], rest[header_size+1:]
        headers = self.parse_scgi_headers(headers_data.decode())
        return headers, body

    def parse_scgi_headers(self, headers_data):
        headers = {}
        parts = headers_data.split('\x00')
        for i in range(0, len(parts) - 1, 2):
            headers[parts[i]] = parts[i + 1]
        return headers

    def produce(self, headers, body):
        raise NotImplementedError("Subclasses must implement this method")

class MySCGIHandler(SCGIHandler):
    def produce(self, headers, body):
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
        self.conn.sendall(response.encode('utf-8'))
        self.conn.close()

class SCGIServer:
    def __init__(self, host, port, handler_class):
        self.host = host
        self.port = port
        self.handler_class = handler_class

    def serve(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"SCGI server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            handler = self.handler_class(client_socket)
            handler.handle()

def main():
    server = SCGIServer('127.0.0.1', 4000, MySCGIHandler)
    server.serve()

if __name__ == "__main__":
    main()
```

## Добавлю
Протокол - просто текст, данные, как угодно называть можно. Просто набор ибучих симовло, и то как мы их обрабатываем на сервере(сервер-приложения) и на клиентской(стороне веб-сервера).<br>

Строка примера указанная в самом начале ридми, получается из сокета, и есть наш запрос протокола SCGI<br>

`data = client_socket.recv(4096)` (4096 - длинна данных, которая будет считываться в байтах. )<br>

Реализация мультипоточности, форков и прочего, не зависит вообще от протокола и реализуется в самих библиотеках. это к слову о fcgid, который не поддерживает многопоточку и fastcgi модулях апача. Их написали так что один не поддерживает а другой - да.

# README - Конфигурация Nginx для SCGI

## Введение

В этом руководстве мы рассмотрим, как настроить Nginx для работы с SCGI-приложением. 

Конфигурация Nginx

Пример конфигурационного файла Nginx для работы с SCGI:

```nginx
server {
    listen 80;
    server_name _;

    location /scgi {
        include scgi_params;
        scgi_pass 127.0.0.1:4000;
    }
}
```

Тестирование: (из папки http_load)
```
./http_load -verbose -parallel 20 -fetches 20 scgi
```

```bash
curl http://your_domain.com/scgi
```

Ссылки на документацию по SCGI

- Модуль SCGI python: [https://github.com/nascheme/scgi/tree/main](https://github.com/nascheme/scgi/tree/main)
- Руководство по SCGI: [https://github.com/nascheme/scgi/blob/main/doc/guide.html](https://github.com/nascheme/scgi/blob/main/doc/guide.html)
- Спецификация SCGI: [https://python.ca/scgi/protocol.txt](https://python.ca/scgi/protocol.txt)

