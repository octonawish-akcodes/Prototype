# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import cache

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        # http://localhost:8080/?https%3A//lava.sirena.org.uk/scheduler/job/179325/log_file/plain
        # urllib.parse.quote() - for encoding
        path = cache.fetch_file("https://lava.sirena.org.uk/scheduler/job/179230/log_file/plain")
        with open(path, "br") as file:
            self.wfile.write(file.read())

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
