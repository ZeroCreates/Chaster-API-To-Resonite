import os
import requests
import time
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone
from dotenv import load_dotenv, set_key
from flask import Flask

load_dotenv()

ENV_FILE = ".env"

cached_end_date = None
last_fetch = 0
CACHE_TIME = 30

app = Flask(__name__)

def format_remaining(end_date):
    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    remaining = end - now
    seconds = int(remaining.total_seconds())

    if seconds < 0:
        return "0s"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{days}d {hours}h {minutes}m {seconds}s"


def fetch_locks(token):
    url = "https://api.chaster.app/locks?status=active"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(url, headers=headers)

    return r.json()


def fetch_end_date(token, lock_id):
    global cached_end_date, last_fetch

    if time.time() - last_fetch < CACHE_TIME:
        return cached_end_date

    url = f"https://api.chaster.app/locks/{lock_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(url, headers=headers)

    cached_end_date = r.json()["endDate"]
    last_fetch = time.time()

    return cached_end_date


def start_api():
    app.run(port=5000)


@app.route("/timeleft")
def timeleft():
    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if not token or not lock_id:
        return "Not configured"

    end_date = fetch_end_date(token, lock_id)

    return format_remaining(end_date)


# GUI
root = tk.Tk()
root.title("Chaster Timer")

token_label = tk.Label(root, text="API Token")
token_label.pack()

token_entry = tk.Entry(root, width=50)
token_entry.pack()

lock_dropdown = ttk.Combobox(root)
lock_dropdown.pack()

locks = []


def load_locks():
    global locks

    token = token_entry.get()

    locks = fetch_locks(token)

    options = []

    for lock in locks:
        options.append(f"{lock['_id']} | {lock['endDate']}")

    lock_dropdown["values"] = options


def save_lock():
    token = token_entry.get()
    selected = lock_dropdown.current()

    lock_id = locks[selected]["_id"]

    set_key(ENV_FILE, "CHASTER_TOKEN", token)
    set_key(ENV_FILE, "LOCK_ID", lock_id)


def update_timer():
    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if token and lock_id:
        end_date = fetch_end_date(token, lock_id)
        remaining = format_remaining(end_date)
        timer_label.config(text=remaining)

    root.after(1000, update_timer)


fetch_button = tk.Button(root, text="Fetch Locks", command=load_locks)
fetch_button.pack()

save_button = tk.Button(root, text="Save Lock", command=save_lock)
save_button.pack()

timer_label = tk.Label(root, text="Not configured", font=("Arial", 20))
timer_label.pack()

threading.Thread(target=start_api, daemon=True).start()

update_timer()

root.mainloop()