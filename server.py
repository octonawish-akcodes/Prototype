from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import cache

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        
        encoded_url = self.path[1:]  # Remove the leading '/' from the encoded URL
        
        url = urllib.parse.unquote(encoded_url)  # Decode the URL
        
        path = cache.fetch_file(url)
        if path:
            with open(path, "br") as file:
                self.wfile.write(file.read())
        else:
            self.wfile.write(b"")  # Empty response if URL is not in cache

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
