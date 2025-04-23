from http.server import BaseHTTPRequestHandler
from app import app
from flask import Flask, Response
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        environ = {
            'wsgi.input': self.rfile,
            'wsgi.errors': os.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https' if self.headers.get('X-Forwarded-Proto') == 'https' else 'http',
            'REQUEST_METHOD': self.command,
            'PATH_INFO': self.path,
            'QUERY_STRING': '',
            'CONTENT_TYPE': self.headers.get('content-type', ''),
            'CONTENT_LENGTH': self.headers.get('content-length', ''),
            'REMOTE_ADDR': self.client_address[0],
            'SERVER_NAME': self.server.server_name,
            'SERVER_PORT': str(self.server.server_port),
            'SERVER_PROTOCOL': self.request_version
        }

        for key, value in self.headers.items():
            key = 'HTTP_' + key.replace('-', '_').upper()
            environ[key] = value

        def start_response(status, headers):
            self.send_response(int(status.split(' ')[0]))
            for header, value in headers:
                self.send_header(header, value)
            self.end_headers()

        response_body = b''
        for data in app(environ, start_response):
            response_body += data

        return response_body

    def do_POST(self):
        return self.do_GET()
