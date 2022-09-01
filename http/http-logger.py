#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import ssl
import sys


ARGS = None


class HTTPServerV6(HTTPServer):
    address_family = socket.AF_INET6


class LoggingHTTPRequestHandler(BaseHTTPRequestHandler):
    def _handle_request(self):
        head = f"""{self.requestline}\r\n{self.headers}"""
        size = self.headers['Content-Length']
        if size:
            body = self.rfile.read(int(size))

        response_size = 0
        if ARGS.response_body:
            response_body = ARGS.response_body.encode()
            response_size = len(response_body)

        print('='*80)
        self.send_response(ARGS.response_code)
        for h in ARGS.response_headers:
            self.send_header(*h.split(':', maxsplit=1))
        self.send_header('Content-Length', response_size)
        self.end_headers()
        if ARGS.response_body:
            self.wfile.write(response_body)
        print('-'*80)

        sys.stdout.write(head)
        if size:
            sys.stdout.buffer.write(body)
            sys.stdout.buffer.flush()
            sys.stdout.write('\r\n')
        print()

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


def main():
    with HTTPServerV6(("", ARGS.port), LoggingHTTPRequestHandler) as httpd:
        try:
            if ARGS.tls_cert:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(ARGS.tls_cert, ARGS.tls_key)
                httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Log incoming HTTP requests including headers and body")
    argparser.add_argument('--port', '-p', type=int, help="Port to listen on (defaults to 80 or 443)")
    argparser.add_argument('--tls-cert', help="Certificate file for TLS")
    argparser.add_argument('--tls-key', help="Private key file for TLS")
    argparser.add_argument('--response-code', '-C', type=int, default=200, help="HTTP response code to return (default: 200)")
    argparser.add_argument('--response-headers', '-H', nargs='*', default=[], help="HTTP response headers to include ('Header:Value' ...)")
    argparser.add_argument('--response-body', '-B', help="HTTP response body to send")
    parsed_args = argparser.parse_args()

    if (parsed_args.tls_cert and not parsed_args.tls_key) or (parsed_args.tls_key and not parsed_args.tls_cert):
        argparser.error("--tls-cert and --tls-key are required both for TLS support")

    if not parsed_args.port:
        if parsed_args.tls_cert:
            parsed_args.port = 443
        else:
            parsed_args.port = 80

    ARGS = parsed_args
    main()
