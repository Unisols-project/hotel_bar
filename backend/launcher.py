"""
Hotel Bar Billing - Desktop Launcher
-------------------------------------
Ha ek file backend (Flask) + frontend (static server) donhi ek process madhye
suru karto, ani browser automatically ughadto. Hyachi .exe bantana (build_exe.bat
vaparun) double-click varun tumhala full app suru hoil.

Requirements before first run:
  1. MySQL install ani suru asel pahije.
  2. backend/database.sql ek vela import kelela asel pahije
     (setup_database.bat run kara, kinva mysql -u root -p < backend/database.sql).
  3. backend/.env madhe barobar DB_PASSWORD set kela asel pahije.
"""

import os
import sys
import time
import shutil
import socket
import threading
import webbrowser
import http.server
import socketserver

# ---------------------------------------------------------------------------
# Path resolution: works both as a plain .py script AND as a PyInstaller .exe
# ---------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT", "8000"))
BACKEND_PORT = int(os.environ.get("PORT", "5000"))


def ensure_env_file():
    env_path = os.path.join(BACKEND_DIR, ".env")
    example_path = os.path.join(BACKEND_DIR, ".env.example")
    if not os.path.exists(env_path) and os.path.exists(example_path):
        shutil.copy(example_path, env_path)
        print("backend/.env navin banavla .env.example varun. Kripaya tyat")
        print("tumcha khara DB_PASSWORD takun app pun suru kara.")


def port_is_open(port, host="127.0.0.1"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def run_backend():
    """Flask app la thread madhe, debug/reloader band karun run karto."""
    ensure_env_file()
    os.chdir(BACKEND_DIR)
    sys.path.insert(0, BACKEND_DIR)
    # app.py module import karto (backend cwd madhun .env, dotenv load hoto)
    import app as backend_module

    try:
        backend_module._check_db_config()
    except Exception as exc:  # noqa: BLE001
        print("MySQL / .env tapasa:", exc)

    backend_module.app.run(
        host="127.0.0.1",
        port=BACKEND_PORT,
        debug=False,
        use_reloader=False,
        threaded=True,
    )


def run_frontend():
    os.chdir(FRONTEND_DIR)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

        def log_message(self, fmt, *args):  # quiet console
            pass

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer(("0.0.0.0", FRONTEND_PORT), Handler) as httpd:
        httpd.serve_forever()


def open_browser_when_ready():
    for _ in range(60):
        if port_is_open(BACKEND_PORT) and port_is_open(FRONTEND_PORT):
            break
        time.sleep(0.5)
    webbrowser.open(f"http://127.0.0.1:{FRONTEND_PORT}")


def main():
    print("=" * 60)
    print(" Hotel Bar Billing App suru hote aahe...")
    print(" Ha window band karu naka jopryant app vaparat aahat.")
    print("=" * 60)

    t_frontend = threading.Thread(target=run_frontend, daemon=True)
    t_frontend.start()

    t_browser = threading.Thread(target=open_browser_when_ready, daemon=True)
    t_browser.start()

    try:
        run_backend()  # main thread var, Ctrl+C ne band karta yeto
    except KeyboardInterrupt:
        print("\nApp band kartoy...")


if __name__ == "__main__":
    main()