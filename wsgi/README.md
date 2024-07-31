## Схема вызовов при использовании WSGI сервера
Пример брался отсюда
> https://github.com/python/cpython/blob/main/Lib/wsgiref/simple_server.py

wsgi - приложеие (вместо того что по ссылке)
```
if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = WSGIServer(server_address, simple_app)
    print(f"Serving on port 8000...")
    httpd.serve_forever()
```
Упрощенный список вызово и операций

WSGIServer
- serve_forever(): слушает входящие соединения.

TCPServer
- get_request(): принимает соединение, возвращает (request, client_address).

BaseRequestHandler
- __init__(request, client_address, self): инициализирует хендлер, устанавливает self.rfile и self.wfile.

WSGIRequestHandler
- handle(): создает ServerHandler с self.rfile, self.wfile, вызывает handler.run(app).

ServerHandler
- run(app): выполняет WSGI-приложение, отправляет заголовки и данные ответа через self.wfile.

### с коментами
```
1. WSGIServer
   └── serve_forever()  # Запуск основного цикла обработки запросов
       └── while True:  # Бесконечный цикл для обработки входящих запросов
           └── _handle_request_noblock()  # Проверка и обработка доступных запросов
               └── request, client_address = self.get_request()  # Получение нового соединения (клиентского сокета)
                   └── get_request(): return self.socket.accept()  # Принятие соединения и возврат клиентского сокета и адреса
               └── self.process_request(request, client_address)  # Обработка запроса: передача на обработку хендлеру
                   └── self.finish_request(request, client_address)  # Завершение обработки запроса
                       └── self.RequestHandlerClass(request, client_address, self)  # Создание экземпляра класса обработчика запросов

2. WSGIRequestHandler (наследуется от StreamRequestHandler)
   └── setup()  # (метод StreamRequestHandler) Установка атрибутов для чтения и записи данных
       └── self.connection = self.request  # Сохранение клиентского сокета как атрибут `connection`
       └── self.rfile = self.connection.makefile('rb', self.rbufsize)  # Создание файла для чтения из сокета
       └── self.wfile = self.connection.makefile('wb', self.wbufsize)  # Создание файла для записи в сокет
   └── handle()  # (метод WSGIRequestHandler) Обработка HTTP-запроса
       └── handler = ServerHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ(), multithread=False)  # Инициализация обработчика WSGI
       └── handler.run(self.server.get_app())  # Запуск WSGI-приложения

3. ServerHandler (SimpleHandler) (наследуется от BaseHandler)
   └── run(application)  # (метод BaseHandler) Запуск WSGI-приложения
       └── self.setup_environ()  # Настройка переменных окружения
           └── env = self.environ = self.os_environ.copy()  # Копирование текущих переменных окружения
           └── self.add_cgi_vars()  # (метод SimpleHandler) Добавление CGI-переменных
               └── self.environ.update(self.base_env)  # base_env = ServerHandler(..., self.get_environ())
       └── self.result = application(self.environ, self.start_response)  # Вызов WSGI-приложения, получение результата
           └── self.start_response()  # Выполняется внутри нашего WSGI-приложения
               └── self.status = status  # Установка статуса ответа
               └── self.headers = self.headers_class(headers)  # Установка заголовков ответа
               └── return self.write  # Возвращает метод для записи тела ответа
       └── self.finish_response()  # Завершение обработки ответа
           └── for data in self.result:  # Итерация по результату из приложения
               └── self.write(data)  # Запись данных в ответ
                   └── self.send_headers()  # Отправка заголовков ответа
                       └── self.send_preamble()  # Отправка статуса и базовых заголовков
                           └── self._write(('HTTP/%s %s\r\n' % (self.http_version, self.status)).encode('iso-8859-1'))  # Отправка строки статуса
                           └── self._write(('Date: %s\r\n' % format_date_time(time.time())).encode('iso-8859-1'))  # Отправка даты
                           └── self._write(('Server: %s\r\n' % self.server_software).encode('iso-8859-1'))  # Отправка информации о сервере
                       └── self._write(bytes(self.headers))  # Отправка заголовков
                   └── self._write(data)  # Отправка тела ответа
                       └── result = self.stdout.write(data)  # Запись данных в клиентский сокет

```
### без комментов
```
1. WSGIServer
   └── serve_forever()
       └── while True:
           └── _handle_request_noblock()
               └── request, client_address = self.get_request()
                   └── get_request(): return self.socket.accept()
               └── self.process_request(request, client_address)
                   └── self.finish_request(request, client_address)
                       └── self.RequestHandlerClass(request, client_address, self)

2. WSGIRequestHandler (наследуется от StreamRequestHandler)
   └── setup() # (метод StreamRequestHandler)
       └── self.connection = self.request
       └── self.rfile = self.connection.makefile('rb', self.rbufsize)
       └── self.wfile = self.connection.makefile('wb', self.wbufsize)
   └── handle() # (метод WSGIRequestHandler)
       └── handler = ServerHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ(), multithread=False)
       └── handler.run(self.server.get_app())

3. ServerHandler (SimpleHandler) (наследуется от BaseHandler)
   └── run(application) # (метод BaseHandler)
       └── self.setup_environ()
           └── env = self.environ = self.os_environ.copy()
           └── self.add_cgi_vars() (метод SimpleHandler)
               └── self.environ.update(self.base_env) # base_env = ServerHandler(..., self.get_environ())
       └── self.result = application(self.environ, self.start_response) # вызывает WSGI-приложение
           └── self.start_response() # выполняется внутри нашего WSGI-приложения
               └── self.status = status
               └── self.headers = self.headers_class(headers)
               └── return self.write  # возвращает self.write для записи тела ответа
       └── self.finish_response()
           └── for data in self.result: # итерируемся по результату из приложения
               └── self.write(data)
                   └── self.send_headers()
                       └── self.send_preamble() # отправка статуса и прочего
                           └── self._write(('HTTP/%s %s\r\n' % (self.http_version, self.status)).encode('iso-8859-1'))
                           └── self._write(('Date: %s\r\n' % format_date_time(time.time())).encode('iso-8859-1'))
                           └── self._write(('Server: %s\r\n' % self.server_software).encode('iso-8859-1'))
                       └── self._write(bytes(self.headers))  # отправка заголовков
                   └── self._write(data)
                       └── result = self.stdout.write(data) # отправка тела ответа

```
### немного обрезанная
```
WSGIServer
    └── serve_forever()
        └── while True:
            └── _handle_request_noblock()
                └── get_request() -> return self.socket.accept()
                └── self.process_request(request, client_address)
                    └── self.finish_request(request, client_address)
                        └── self.RequestHandlerClass(request, client_address, self)
                            └── setup() (StreamRequestHandler)
                                └── self.connection = self.request
                                └── self.rfile = self.connection.makefile('rb', self.rbufsize)
                                └── self.wfile = self.connection.makefile('wb', self.wbufsize)
                            └── handle() (WSGIRequestHandler)
                                └── handler = ServerHandler(self.rfile, self.wfile, self.get_stderr(), self.get_environ(), multithread=False)
                                └── handler.run(self.server.get_app())
                                    └── run(application) (BaseHandler)
                                        └── self.setup_environ()
                                        └── self.result = application(self.environ, self.start_response)
                                            └── self.start_response()
                                                └── self.status = status
                                                └── self.headers = self.headers_class(headers)
                                                └── return self.write
                                        └── self.finish_response()
                                            └── for data in self.result:
                                                └── self.write(data)
                                                    └── self.send_headers()
                                                        └── self.send_preamble()
                                                            └── self._write(bytes(self.headers))
                                                                └── result = self.stdout.write(data)

```

### Немного упрощенный скрипт из примера
```
from http.server import BaseHTTPRequestHandler, HTTPServer
import io
import sys

class WSGIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        environ = self.get_environ()
        response_body = []

        def start_response(status, response_headers):
            self.send_response(int(status.split()[0]))
            for header_name, header_value in response_headers:
                self.send_header(header_name, header_value)
            self.end_headers()

        result = self.server.application(environ, start_response)
        try:
            for data in result:
                response_body.append(data)
            response_body = b''.join(response_body)
            self.wfile.write(response_body)
        finally:
            if hasattr(result, 'close'):
                result.close()

    def get_environ(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': io.BytesIO(self.rfile.read(int(self.headers.get('Content-Length', 0)))),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.command,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.server.server_name,
            'SERVER_PORT': str(self.server.server_port),
            'SERVER_PROTOCOL': self.request_version,
        }
        for key, value in self.headers.items():
            key = key.replace('-', '_').upper()
            if 'HTTP_' + key not in env:
                env['HTTP_' + key] = value
        return env

class WSGIServer(HTTPServer):
    def __init__(self, server_address, application):
        super().__init__(server_address, WSGIRequestHandler)
        self.application = application

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Hello, World!']

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = WSGIServer(server_address, simple_app)
    print(f"Serving on port 8000...")
    httpd.serve_forever()
```

Создание файла из сокета (makefile):

Метод makefile() используется для создания файлового объекта, который привязан к сокету. Этот файловый объект предоставляет удобный интерфейс для работы с сокетом, используя методы чтения и записи файлов, такие как read(), write(), и так далее.
self.rfile и self.wfile не создают новые сокеты, а создают файловые объекты, которые обёртывают существующий сокет self.connection.
