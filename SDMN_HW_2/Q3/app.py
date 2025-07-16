#!/usr/bin/env python3

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import argparse

class StatusHTTPServer(ThreadingMixIn, HTTPServer):
    """
    HTTP server that stores a mutable status message.
    """
    def __init__(self, server_address, RequestHandlerClass, initial_status="OK"):
        super().__init__(server_address, RequestHandlerClass)
        self.status_message = initial_status

class StatusHandler(BaseHTTPRequestHandler):
    ROUTE = "/api/v1/status"

    def send_json(self, code, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = json.dumps(payload).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != self.ROUTE:
            return self.send_error(404, "Not Found")
        # Always return 200 OK for GET
        payload = {"status": self.server.status_message}
        self.send_json(200, payload)

    def do_POST(self):
        if self.path != self.ROUTE:
            return self.send_error(404, "Not Found")
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            return self.send_error(411, "Length Required")
        try:
            length = int(content_length)
            body = self.rfile.read(length)
            data = json.loads(body)
        except (ValueError, json.JSONDecodeError):
            return self.send_error(400, "Bad Request")

        if "status" not in data or not isinstance(data["status"], str):
            return self.send_error(400, "Invalid JSON payload")

        # Update server state
        self.server.status_message = data["status"]
        payload = {"status": self.server.status_message}
        # Return created
        self.send_json(201, payload)

    def log_message(self, format, *args):
        # Override to reduce console noise
        return

def main():
    parser = argparse.ArgumentParser(description="Simple status HTTP API server.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    server = StatusHTTPServer((args.host, args.port), StatusHandler)
    print(f"Starting server at http://{args.host}:{args.port}{StatusHandler.ROUTE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.server_close()

if __name__ == "__main__":
    main()
