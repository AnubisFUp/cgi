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

