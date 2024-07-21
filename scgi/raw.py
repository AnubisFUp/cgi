import socket  # Импортируем модуль socket для работы с сетевыми соединениями

def parse_scgi_headers(data):
    headers = {}  # Создаем пустой словарь для хранения заголовков
    parts = data.split('\x00')  # Разбиваем строку данных по нулевым байтам ('\x00')
    print("Parts: ", parts)
    for i in range(0, len(parts) - 1, 2):
        headers[parts[i]] = parts[i + 1]  # Записываем пары ключ-значение в словарь
    return headers  # Возвращаем словарь заголовков

def main():
    host = '127.0.0.1'  # Задаем хост для сервера (localhost)
    port = 4000  # Задаем порт для сервера

    # Создаем серверный сокет (IPv4, потоковый сокет)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Привязываем сокет к хосту и порту
    server_socket.listen(5)  # Начинаем слушать соединения (максимум 5 одновременных соединений)
    print(f"SCGI server listening on {host}:{port}")  # Выводим сообщение о запуске сервера

    while True:  # Бесконечный цикл для обработки входящих соединений
        client_socket, client_address = server_socket.accept()  # Принимаем новое соединение
        print(f"Connection from {client_address}")  # Выводим адрес клиента

        # Получаем данные от клиента
        data = client_socket.recv(4096)  # Считываем данные из сокета (максимум 4096 байт)
        print("Raw data received:")  # Выводим сообщение о получении данных
        print(data)  # Выводим сырые байтовые данные

        # Декодируем байтовые данные в строку
        data_str = data.decode('utf-8', errors='replace')
        print(f"Length of data_str: {len(data_str)}")  # Выводим длину строки

        # Замена нулевых байтов на видимые символы "<NUL>"
        visible_data_str = data_str.replace('\x00', '<NUL>')
        print("Visible data string:")
        print(visible_data_str)  # Выводим строку с замененными нулевыми байтами

        # Разделяем строку на размер заголовка и остальную часть данных
        header_size_str, rest = data_str.split(':', 1)
        header_size = int(header_size_str)  # Преобразуем размер заголовка в целое число

        # Разделяем данные на заголовки и тело запроса
        headers_data, body = rest[:header_size], rest[header_size+1:]
        headers = parse_scgi_headers(headers_data)  # Парсим заголовки в словарь

        print("\nParsed SCGI headers:")  # Выводим сообщение о начале вывода заголовков
        for key, value in headers.items():  # Проходим по всем заголовкам
            print(f"{key}: {value}")  # Выводим каждый заголовок

        print("\nBody:")  # Выводим сообщение о начале вывода тела запроса
        print(body)  # Выводим тело запроса

        client_socket.close()  # Закрываем соединение с клиентом

if __name__ == "__main__":
    main()  # Запускаем основную функцию

