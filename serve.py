import http.server
import socketserver

# Define the port you want to use (e.g., 8000)
port = 8501

Handler = http.server.SimpleHTTPRequestHandler

class CustomHandler(Handler):
    def do_GET(self):
        # If the requested URL does not map to a file, serve the index.html file
        if not "." in self.path:
            self.path = '/index.html'
        return super().do_GET()

with socketserver.TCPServer(("", port), CustomHandler) as httpd:
    print(f"Serving at http://127.0.0.1:{port}")
    httpd.serve_forever()