import time
import threading

def _tick_loop():
    while True:
        print("Tick")
        time.sleep(1.0)

def start_scheduler():
    """Starts the background ticker thread."""
    thread = threading.Thread(target=_tick_loop, daemon=True)
    thread.start()