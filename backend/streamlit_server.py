import threading
import time

import requests
import uvicorn

_server = None
_thread = None


def start_api_server():
    global _server, _thread

    if _thread is not None and _thread.is_alive():
        return

    config = uvicorn.Config(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning"
    )

    _server = uvicorn.Server(config)

    _thread = threading.Thread(
        target=_server.run,
        daemon=True
    )

    _thread.start()

    for _ in range(30):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/health",
                timeout=1
            )

            if response.status_code == 200:
                return

        except requests.RequestException:
            pass

        time.sleep(1)

    raise RuntimeError(
        "FastAPI n'a pas démarré correctement."
    )