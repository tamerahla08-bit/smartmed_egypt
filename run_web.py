"""Run the web app on your own computer:  python run_web.py   (open http://localhost:8000)
Phones on the same Wi-Fi can open http://<your-laptop-IP>:8000 (printed below)."""
import os, socket
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
from webapp import application
from knowledge_base import APP_NAME, APP_SUBTITLE

class Threaded(ThreadingMixIn, WSGIServer):
    daemon_threads = True

class Quiet(WSGIRequestHandler):
    def log_message(self, *a): pass

def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("10.255.255.255", 1)); ip = s.getsockname()[0]; s.close(); return ip
    except OSError:
        return "your-laptop-IP"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"{APP_NAME} - {APP_SUBTITLE}\n(web version) is running.\n  On this computer : http://localhost:{port}\n  On your phone (same Wi-Fi): http://{lan_ip()}:{port}\nPress Ctrl+C to stop.")
    make_server("0.0.0.0", port, application, server_class=Threaded, handler_class=Quiet).serve_forever()
