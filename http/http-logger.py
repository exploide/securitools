#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import sys


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


class LoggingHTTPRequestHandler(BaseHTTPRequestHandler):
    def _handle_request(self):
        print()
        print('='*80)
        self.send_response(200)
        self.end_headers()
        print('-'*80)
        head = f"""{self.requestline}\r\n{self.headers}"""
        sys.stdout.write(head)
        size = self.headers['Content-Length']
        if size:
            body = self.rfile.read(int(size))
            sys.stdout.buffer.write(body)
            sys.stdout.buffer.flush()
            sys.stdout.write('\r\n')

    def do_GET(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_CONNECT(self):
        self._handle_request()

    def do_OPTIONS(self):
        self._handle_request()

    def do_TRACE(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()


def main(args):
    with HTTPServerV6(("", args.port), LoggingHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Log incoming HTTP requests including headers and body", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('--port', '-p', type=int, default=80, help="Port to listen on")
    parsed_args = argparser.parse_args()
    main(parsed_args)
