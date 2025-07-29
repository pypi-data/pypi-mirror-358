import datetime

def log_event(to, status, error=None):
    log_line = f"[{datetime.datetime.now()}] TO: {to} STATUS: {status}"
    if error:
        log_line += f" ERROR: {error}"
    with open("openmailer.log", "a") as f:
        f.write(log_line + "\n")