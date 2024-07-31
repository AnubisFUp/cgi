import time
import os

def app(environ, start_response):
    """Simplest possible application object"""
    pid = os.getpid()
    data = b'Hello, World!\n' + str(pid).encode()  # Convert pid to bytes
    status = '200 OK'
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    time.sleep(1)
    return iter([data])

