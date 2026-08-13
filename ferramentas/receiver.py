import http.server, os, re, sys

OUT = os.path.join(os.path.dirname(__file__), '..', 'fotos')
os.makedirs(OUT, exist_ok=True)

class H(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        ctype = self.headers.get('Content-Type', '')
        m = re.search(r'boundary=(.+)', ctype)
        if m:
            boundary = m.group(1).encode()
            parts = data.split(b'--' + boundary)
            for p in parts:
                if b'filename="' in p:
                    fn = re.search(rb'filename="([^"]+)"', p).group(1).decode()
                    body = p.split(b'\r\n\r\n', 1)[1].rsplit(b'\r\n', 1)[0]
                    fn = re.sub(r'[^\w.\-]', '_', fn)
                    with open(os.path.join(OUT, fn), 'wb') as f:
                        f.write(body)
                    print(f'saved {fn} {len(body)} bytes', flush=True)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self, *a):
        pass

http.server.HTTPServer(('127.0.0.1', 8765), H).serve_forever()
