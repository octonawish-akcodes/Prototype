from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import os

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    file_directory = "/home/abhishek/Downloads/files/"

    def _set_response(self, status_code=200, content_type="text/plain"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)

    def serve_file(self, file_path):
        try:
            with open(file_path, "rb") as file:
                content = file.read()
                self.wfile.write(content)
        except FileNotFoundError:
            self._set_response(404)
            self.wfile.write(b"File not found")

    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/no_content_disposition":
            self._set_response()
            
            self.end_headers()
            self.serve_file(os.path.join(self.file_directory, "pol.yaml"))

        elif parsed_url.path == "/content_disposition_without_filename":
            self._set_response()
            self.send_header("Content-Disposition", 'attachment')
            self.end_headers()
            self.serve_file(os.path.join(self.file_directory, "tasks.txt"))

        elif parsed_url.path == "/content_disposition":
            self._set_response()
            self.send_header("Content-Disposition", 'attachment; filename="different_filename"')
            self.end_headers()
            self.serve_file(os.path.join(self.file_directory, "res.yaml"))

        elif parsed_url.path == "/redirect_from":
            self._set_response(status_code=302)
            self.send_header("Location", "/redirect_to")
            self.end_headers()

        elif parsed_url.path == "/redirect_to":
            self._set_response()
            self.end_headers()
            self.serve_file(os.path.join(self.file_directory, "res.yaml"))

        else:
            self._set_response(404)
            self.end_headers()
            self.wfile.write(b"Invalid URL")

    def do_HEAD(self):
        self.do_GET()


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
