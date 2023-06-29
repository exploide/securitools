#!/usr/bin/env python3

"""
A simple HTTP to websocket proxy.

Starts an HTTP server and listens to incoming POST requests.
The request body is then forwarded to a given websocket URL.
The response of the websocket message is returned as the HTTP response.

This can be useful when analyzing a websocket endpoint for security
issues but the desired attack tool only supports sending HTTP requests.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ssl
import sys

try:
    from websocket import create_connection, WebSocketConnectionClosedException
except ModuleNotFoundError:
    print("Error: Missing dependency websocket-client", file=sys.stderr)
    sys.exit(1)


ARGS = None


class WsProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_websocket_message(self, target, data):
        ws = create_connection(target, **ARGS.connect_args)
        if ARGS.init_send:
            ws.send(ARGS.init_send)
            ws.recv()
        ws.send(data)
        response = ws.recv()
        ws.close()
        return response

    def do_POST(self):
        size = self.headers['Content-Length']
        if size:
            data = self.rfile.read(int(size))
        else:
            self.send_response(411)
            self.end_headers()
            self.wfile.write(b"Proxy error: Set a Content-Length header and send data in the POST body.")
            return

        try:
            ws_response = self._send_websocket_message(ARGS.target, data)
        except WebSocketConnectionClosedException:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b"Proxy error: Websocket server prematurely closed the connection.")
            return

        self.send_response(200)
        self.send_header('Content-Length', len(ws_response))
        self.end_headers()
        self.wfile.write(ws_response)


def main():
    with ThreadingHTTPServer((ARGS.address, ARGS.port), WsProxyHTTPRequestHandler) as httpd:
        try:
            print(f"Listening on http://{ARGS.address}:{ARGS.port} for incoming requests...")
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Proxy incoming HTTP requests to a remote websocket", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument('--address', default="127.0.0.1", help="Address for the HTTP server to listen on")
    argparser.add_argument('--port', '-p', type=int, default=8080, help="Port for the HTTP server to listen on")
    argparser.add_argument('--no-cert-check', action="store_true", default=False, help="Disable TLS certificate checks")
    argparser.add_argument('--upstream-proxy', type=str, help="Upstream proxy URL (supports http, socks4, socks4a, socks5, socks5h)")
    argparser.add_argument('--init-send', type=str, metavar="MESSAGE", help="Initial message to send after each new connection (e.g. authentication)")
    argparser.add_argument('target', help="Websocket URL to proxy to")
    parsed_args = argparser.parse_args()


    parsed_args.connect_args = {}

    if parsed_args.no_cert_check:
        parsed_args.connect_args["sslopt"] = {"cert_reqs": ssl.CERT_NONE}

    if parsed_args.upstream_proxy:
        try:
            scheme, proxy = parsed_args.upstream_proxy.split("://", maxsplit=1)
            if scheme not in ("http", "socks4", "socks4a", "socks5", "socks5h"):
                argparser.error("Invalid scheme for upstream proxy.")
            host, port = proxy.split(":", maxsplit=1)
        except ValueError:
            argparser.error("Invalid format for upstream proxy, must be scheme://host:port.")
        parsed_args.connect_args["proxy_type"] = scheme
        parsed_args.connect_args["http_proxy_host"] = host
        parsed_args.connect_args["http_proxy_port"] = port

    ARGS = parsed_args
    main()
