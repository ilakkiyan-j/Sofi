import threading

silent_mode = False
lock = threading.Lock()

def log(*args, **kwargs):
    if silent_mode:
        return
    with lock:
        print(*args, **kwargs)
