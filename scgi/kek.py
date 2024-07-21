#!/usr/bin/python3
from scgi import scgi_server
import os
from threading import Lock

# Глобальный счетчик запросов и блокировка для синхронизации
request_counter = 0
counter_lock = Lock()

class MySCGIHandler(scgi_server.SCGIHandler):
    def produce(self, env, content_length, input_stream, output_stream):
        global request_counter

        # Синхронизация увеличения счетчика запросов
        with counter_lock:
            request_counter += 1
            current_request_number = request_counter

        # Получение PID процесса
        process_id = os.getpid()

        # Формирование HTTP-заголовка и тела ответа
        response_body = f"PID: {process_id} RN: {current_request_number}"
        response = f"Content-Type: text/plain\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"

        # Отправка ответа
        output_stream.write(response.encode('utf-8'))

def main():
    #server = scgi_server.SCGIServer(handler_class=MySCGIHandler, port=4000, max_children=1)
    server = scgi_server.SCGIServer(port=4000, max_children=1)
    server.serve()

if __name__ == "__main__":
    main()

