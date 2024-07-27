import socket
import struct

class UwsgiServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"uWSGI server listening on {self.host}:{self.port}")

        while True:
            client_socket, address = server_socket.accept()
            print(f"Connection from {address}")
            self.handle_request(client_socket)
            client_socket.close()

    def handle_request(self, client_socket):
        # Read the 4-byte header
        header = client_socket.recv(4)
        print(f"Header: {header}")  # Print the raw header for debugging
        mod1, size, mod2 = struct.unpack('<BHB', header)

        print(f"Received var block size: {size}")

        # Read the var block
        var_block = self.recv_all(client_socket, size)
        print(f"Raw var_block content: {var_block}")
        print(f"Len of var_block content: {len(var_block)}")
        if len(var_block) != size:
            print(f"Warning: Expected var block size {size}, but got {len(var_block)}")

        env = self.parse_var_block(var_block)
        
        # Read the body if CONTENT_LENGTH is specified
        body = None
        if 'CONTENT_LENGTH' in env and env['CONTENT_LENGTH'].isdigit():
            content_length = int(env['CONTENT_LENGTH'])
            body = self.recv_all(client_socket, content_length)

        print("Environment variables:")
        for k, v in env.items():
            print(f"{k}: {v}")

        print("Request body:")
        if body:
            print(body.decode('utf-8'))

        # Send a response
        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"
        client_socket.sendall(response)

    def recv_all(self, client_socket, length):
        data = b''
        while len(data) < length:
            more = client_socket.recv(length - len(data))
            if not more:
                raise EOFError(f'Was expecting {length} bytes but only received {len(data)} bytes before the connection closed.')
            data += more
        return data

    def parse_var_block(self, var_block):
        env = {}
        i = 0
        while i < len(var_block):

            key_length = struct.unpack('<H', var_block[i:i+2])[0]
            i += 2
            # print(f"key_length: {key_length}")
            
            key = var_block[i:i+key_length].decode('utf-8')
            i += key_length
            # print(f"key: {key}")

            value_length = struct.unpack('<H', var_block[i:i+2])[0]
            i += 2
            # print(f"value_length: {value_length}")
            
            value = var_block[i:i+value_length].decode('utf-8')
            i += value_length
            # print(f"value: {value}")

            env[key] = value

        return env

if __name__ == "__main__":
    server = UwsgiServer('0.0.0.0', 4040)
    server.start()

