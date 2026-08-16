import sys
import threading

silent_mode = False
lock = threading.Lock()

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def log(*args, **kwargs):
    if silent_mode:
        return
    with lock:
        try:
            print(*args, **kwargs)
        except UnicodeEncodeError:
            safe_args = [str(a).encode('ascii', errors='replace').decode('ascii') for a in args]
            print(*safe_args, **kwargs)
