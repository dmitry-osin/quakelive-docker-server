from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import minqlx


class healthcheck(minqlx.Plugin):

    def __init__(self):
        super().__init__()
        self.bootstrap_httpd()

    @minqlx.thread
    def bootstrap_httpd(self):
        with TCPServer(("0.0.0.0", 9999), healthcheck.HTTPRequestHandler) as server:
            server.serve_forever()

    class HTTPRequestHandler(SimpleHTTPRequestHandler):

        def do_GET(self):
            self.send_response(200)
            message = bytes("ok", 'utf8')

            # Send headers
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Content-length', str(len(message)))
            self.end_headers()

            # Write content as utf-8 data
            self.wfile.write(message)
            return
