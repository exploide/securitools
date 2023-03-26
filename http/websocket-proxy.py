#!/usr/bin/env python3

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys

try:
    from websocket import create_connection
except ModuleNotFoundError:
    print("Error: Missing dependency websocket-client", file=sys.stderr)
    sys.exit(1)


ARGS = None


class WsProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_websocket_message(self, target, data):
        ws = create_connection(target)
        ws.send(data)
        response = ws.recv()
        ws.close()
        return response

    def do_POST(self):
        size = self.headers['Content-Length']
        if size:
            data = self.rfile.read(int(size))
        else:
            data = ""

        ws_response = self._send_websocket_message(ARGS.target, data)
        ws_response = ws_response.encode()

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
    argparser.add_argument('target', help="Websocket URL to proxy to")
    parsed_args = argparser.parse_args()

    ARGS = parsed_args
    main()
