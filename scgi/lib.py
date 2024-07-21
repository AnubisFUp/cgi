import socket
import struct
import os

class SCGIServer:
    def __init__(self, host='127.0.0.1', port=4000, handler_class=None):
        self.host = host
        self.port = port
        self.handler_class = handler_class

    def serve(self):
        # Создаем сокет и связываем его с указанным хостом и портом
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)  # Сервер слушает до 5 одновременных соединений
        print(f"SCGI server listening on {self.host}:{self.port}")

        while True:
            # Принимаем новое соединение
            client_socket, client_address = server_socket.accept()
            # Создаем обработчик для этого соединения
            handler = self.handler_class(client_socket)
            # Обрабатываем соединение
            handler.handle()

class SCGIHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def handle(self):
        # Считываем размер заголовка SCGI
        size = self._read_header_size()
        # Считываем заголовки SCGI
        headers = self._read_headers(size)
        # Считываем тело запроса
        content_length = int(headers.get('CONTENT_LENGTH', 0))
        body = self.client_socket.recv(content_length)

        # Обрабатываем запрос (этот метод должен быть реализован в подклассе)
        self.produce(headers, content_length, body, self.client_socket)

        # Закрываем соединение
        self.client_socket.close()

    def _read_header_size(self):
        # Считываем размер заголовка, который заканчивается двоеточием
        size_str = b""
        while True:
            char = self.client_socket.recv(1)
            if char == b':':
                break
            size_str += char
        size = int(size_str)
        # Пропускаем запятую после размера заголовка
        self.client_socket.recv(1)
        return size

    def _read_headers(self, size):
        # Считываем данные заголовка и разбираем их в словарь
        headers_data = self.client_socket.recv(size).decode('utf-8')
        headers = {}
        items = headers_data.split('\0')
        for i in range(0, len(items) - 1, 2):
            key = items[i]
            value = items[i + 1]
            headers[key] = value
        return headers

    def produce(self, headers, content_length, body, output_stream):
        # Этот метод должен быть реализован в подклассе для обработки запроса
        raise NotImplementedError("Subclasses must implement this method")

# Пример использования библиотеки

import os
from threading import Lock

# Глобальный счетчик запросов и блокировка для синхронизации
request_counter = 0
counter_lock = Lock()

class MySCGIHandler(SCGIHandler):
    def produce(self, headers, content_length, body, output_stream):
        global request_counter
        
        # Синхронизация увеличения счетчика запросов
        with counter_lock:
            request_counter += 1
            current_request_number = request_counter
        
        # Получение PID процесса
        process_id = os.getpid()
        
        # Формирование HTTP-заголовка и тела ответа
        response_body = f"Hello, World!\nPID: {process_id}\nRequest Number: {current_request_number}"
        response = f"Content-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
        
        # Отправка ответа
        output_stream.sendall(response.encode('utf-8'))

def main():
    # Создаем сервер SCGI с указанным обработчиком запросов
    server = SCGIServer(handler_class=MySCGIHandler)
    # Запускаем сервер
    server.serve()

if __name__ == "__main__":
    main()
