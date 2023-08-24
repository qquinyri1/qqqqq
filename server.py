import os
import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class SocketServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.port = 5000

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.host, self.port))
            while True:
                data, _ = s.recvfrom(1024)
                try:
                    data_dict = json.loads(data.decode())
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    data_dict[timestamp] = data_dict.pop("timestamp")
                    with open("storage/data.json", "a") as f:
                        f.write(json.dumps(data_dict) + "\n")
                except Exception as e:
                    print("Error processing data:", e)

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_parts = urlparse(self.path)
        file_path = url_parts.path.strip("/")
        if file_path == "":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open('index.html', 'rb') as fh:
                self.wfile.write(fh.read())
        elif file_path == "message.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open('message.html', 'rb') as fh:
                self.wfile.write(fh.read())
        elif file_path == "style.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open('style.css', "rb") as fh:
                self.wfile.write(fh.read())
        elif file_path == "logo.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open('logo.png', "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open('error.html', "rb") as fh:
                self.wfile.write(fh.read())

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        post_params = parse_qs(post_data.decode())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        post_params["timestamp"] = timestamp
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(json.dumps(post_params).encode(), ("localhost", 5000))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open('message.html','rb') as fh:
            self.wfile.write(fh.read())

def main():
    socket_server = SocketServer()
    socket_server.daemon = True
    socket_server.start()

    server_address = ("localhost", 3000)
    http_server = HTTPServer(server_address, HTTPRequestHandler)
    print("HTTP server started on http://localhost:3000")
    http_server.serve_forever()

if __name__ == "__main__":
    main()
