"""
Frontend static-file server.

Run:
  python serve.py

Then open:
  http://127.0.0.1:8000
"""

import http.server
import os
import socketserver
import sys

PORT = int(os.environ.get("FRONTEND_PORT", "8000"))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    try:
        with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
            print(f"Frontend running: http://127.0.0.1:{PORT}")
            print("Keep this window open. Press Ctrl+C to stop.")
            httpd.serve_forever()
    except OSError as exc:
        if exc.errno == 10048:
            print(f"Port {PORT} is already in use.")
            print(f"Open http://127.0.0.1:{PORT} or stop the old frontend server first.")
            sys.exit(1)
        raise
