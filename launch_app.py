import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

from streamlit.web import cli as stcli


FROZEN = getattr(sys, "frozen", False)

if FROZEN:
    APP_DIR = Path(sys._MEIPASS).resolve()
    CONFIG_DIR = Path(sys.executable).resolve().parent / "backend"
else:
    APP_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = APP_DIR / "backend"

APP_FILE = APP_DIR / "app.py"
BACKEND_DIR = APP_DIR / "backend"


def load_config():
    env_file = CONFIG_DIR / ".env"

    if not env_file.exists():
        raise FileNotFoundError(
            f"Backend configuration not found: {env_file}\n"
            "Place your private .env file in the backend folder."
        )

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value

    if not os.environ.get("APP_ACCESS_TOKEN", "").strip():
        raise RuntimeError("APP_ACCESS_TOKEN is missing from configuration.")

    if not os.environ.get("GROQ_API_KEY", "").strip():
        raise RuntimeError("GROQ_API_KEY is missing from configuration.")


def backend_is_running():
    try:
        with urlopen("http://127.0.0.1:8000/health", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def start_backend():
    if backend_is_running():
        print("Battery AI backend is already running.")
        return

    if not (BACKEND_DIR / "main.py").exists():
        raise FileNotFoundError(
            f"Backend main.py not found: {BACKEND_DIR / 'main.py'}"
        )

    sys.path.insert(0, str(BACKEND_DIR))

    import uvicorn

    def run_server():
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            log_level="warning",
        )

    threading.Thread(target=run_server, daemon=True).start()

    for _ in range(30):
        if backend_is_running():
            print("Battery AI backend started.")
            return
        time.sleep(1)

    raise RuntimeError(
        "Backend did not start. Check configuration and port 8000."
    )


def open_browser():
    time.sleep(5)
    webbrowser.open("http://127.0.0.1:8501/")


def main():
    if not APP_FILE.exists():
        raise FileNotFoundError(f"app.py not found: {APP_FILE}")

    os.chdir(APP_DIR)
    sys.path.insert(0, str(APP_DIR))

    load_config()
    start_backend()

    threading.Thread(target=open_browser, daemon=True).start()

    sys.argv = [
        "streamlit",
        "run",
        str(APP_FILE),
        "--global.developmentMode=false",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
