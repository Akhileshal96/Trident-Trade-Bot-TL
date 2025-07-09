import threading

_bot_running = True
lock = threading.Lock()

def is_bot_running():
    with lock:
        return _bot_running

def stop_bot():
    global _bot_running
    with lock:
        _bot_running = False

def resume_bot():
    global _bot_running
    with lock:
        _bot_running = True
