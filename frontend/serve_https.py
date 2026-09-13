"""Serve the static frontend over HTTPS for local development."""
import http.server
import os
import ssl


class ReusableHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


os.chdir(os.path.dirname(__file__))
server = ReusableHTTPServer(("127.0.0.1", 5500), http.server.SimpleHTTPRequestHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("../.dev-cert/localhost.crt", "../.dev-cert/localhost.key")
server.socket = context.wrap_socket(server.socket, server_side=True)
print("VentureLens frontend: https://127.0.0.1:5500", flush=True)
server.serve_forever()
