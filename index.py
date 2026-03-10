import os
import time
import threading
import requests
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timezone
from dotenv import load_dotenv, set_key
from flask import Flask
# Ensure .env exists
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        f.write("")  # empty file
load_dotenv()

ENV_FILE = ".env"

TOKEN = os.getenv("CHASTER_TOKEN")
LOCK_ID = os.getenv("LOCK_ID")

cached_end_date = None
last_fetch = 0
CACHE_TIME = 30

locks = []

# --- CYBER COLORS ---
BG = "#0a0a0a"
PANEL = "#111111"
CYAN = "#00ffff"
GREEN = "#00ff9c"
TEXT = "#e0e0e0"

app = Flask(__name__)


# ------------------------
# API FUNCTIONS
# ------------------------

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

    data = r.json()

    if data.get("endDate") is None:
        cached_end_date = "HIDDEN"
    else:
        cached_end_date = data["endDate"]

    last_fetch = time.time()

    return cached_end_date


def get_keyholder(lock):

    if "keyholder" in lock and lock["keyholder"]:
        return lock["keyholder"].get("username", "Unknown")

    return "Unknown"


# ------------------------
# TIME FORMAT
# ------------------------

def format_remaining(end_date):

    if end_date == "HIDDEN":
        return "TIMER HIDDEN"

    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    remaining = end - now
    seconds = int(remaining.total_seconds())

    if seconds <= 0:
        return "UNLOCKED"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{days}d {hours}h {minutes}m {seconds}s"


# ------------------------
# LOCAL API
# ------------------------

@app.route("/timeleft")
def timeleft():

    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if not token or not lock_id:
        return "not configured"

    end_date = fetch_end_date(token, lock_id)

    if end_date == "HIDDEN":
        return "hidden"

    return format_remaining(end_date)


def start_api():
    app.run(port=5000)

@app.route("/addtime", methods=["POST"])
def add_time():

    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if not token or not lock_id:
        return jsonify({"error": "Lock not configured"}), 400
    

    milseconds = int(3600000)

    url = f"https://api.chaster.app/locks/{lock_id}/update-time"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "duration": milseconds
    }

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code != 204:
        return jsonify({"error": r.text}), r.status_code

    return jsonify({
        "status": "success",
        "added_milseconds": milseconds
    })

# ------------------------
# GUI
# ------------------------

root = tk.Tk()
root.title("Resonite X Chaster Timer")
root.geometry("520x420")
root.configure(bg=BG)


title = tk.Label(
    root,
    text="CHASTER LOCK TERMINAL",
    bg=BG,
    fg=CYAN,
    font=("Consolas", 18, "bold")
)

title.pack(pady=10)


token_label = tk.Label(
    root,
    text="API TOKEN",
    bg=BG,
    fg=TEXT,
    font=("Consolas", 10)
)

token_label.pack()

token_entry = tk.Entry(
    root,
    width=50,
    bg=PANEL,
    fg=GREEN,
    insertbackground=GREEN,
    relief="flat",
    font=("Consolas", 10)
)

token_entry.pack(pady=5)


if TOKEN:
    token_entry.insert(0, TOKEN)


lock_dropdown = ttk.Combobox(root, width=55)
lock_dropdown.pack(pady=10)


keyholder_label = tk.Label(
    root,
    text="KEYHOLDER: UNKNOWN",
    bg=BG,
    fg=CYAN,
    font=("Consolas", 12, "bold")
)

keyholder_label.pack(pady=5)


# ------------------------
# BUTTON FUNCTIONS
# ------------------------

def load_locks():

    global locks

    token = token_entry.get()

    if not token:
        return

    try:

        locks = fetch_locks(token)

        options = []

        for lock in locks:

            keyholder = get_keyholder(lock)

            label = f"{lock['_id']} | KH: {keyholder}"

            options.append(label)

        lock_dropdown["values"] = options

    except:
        pass


def save_lock():

    token = token_entry.get()

    selected = lock_dropdown.current()

    if selected < 0:
        return

    lock = locks[selected]

    lock_id = lock["_id"]
    keyholder = get_keyholder(lock)

    set_key(ENV_FILE, "CHASTER_TOKEN", token)
    set_key(ENV_FILE, "LOCK_ID", lock_id)

    keyholder_label.config(text=f"KEYHOLDER: {keyholder}")


button_frame = tk.Frame(root, bg=BG)
button_frame.pack(pady=10)


fetch_button = tk.Button(
    button_frame,
    text="FETCH LOCKS",
    command=load_locks,
    bg=PANEL,
    fg=CYAN,
    font=("Consolas", 10, "bold"),
    relief="flat",
    padx=20
)

fetch_button.grid(row=0, column=0, padx=10)


save_button = tk.Button(
    button_frame,
    text="SAVE LOCK",
    command=save_lock,
    bg=PANEL,
    fg=GREEN,
    font=("Consolas", 10, "bold"),
    relief="flat",
    padx=20
)

save_button.grid(row=0, column=1, padx=10)


timer_label = tk.Label(
    root,
    text="NOT CONFIGURED",
    bg=BG,
    fg=GREEN,
    font=("Consolas", 30, "bold")
)

timer_label.pack(pady=40)


# ------------------------
# AUTO LOAD SAVED LOCK
# ------------------------

def auto_load_saved_lock():

    global locks

    token = os.getenv("CHASTER_TOKEN")
    saved_lock = os.getenv("LOCK_ID")

    if not token:
        return

    try:

        locks = fetch_locks(token)

        options = []
        selected_index = None

        for i, lock in enumerate(locks):

            keyholder = get_keyholder(lock)

            label = f"{lock['_id']} | KH: {keyholder}"

            options.append(label)

            if lock["_id"] == saved_lock:
                selected_index = i

        lock_dropdown["values"] = options

        if selected_index is not None:

            lock_dropdown.current(selected_index)

            keyholder = get_keyholder(locks[selected_index])

            keyholder_label.config(text=f"KEYHOLDER: {keyholder}")

    except:
        pass


# ------------------------
# TIMER UPDATE
# ------------------------

def update_timer():

    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if token and lock_id:

        end_date = fetch_end_date(token, lock_id)

        remaining = format_remaining(end_date)

        timer_label.config(text=remaining)

    root.after(1000, update_timer)


# ------------------------
# STARTUP
# ------------------------

threading.Thread(target=start_api, daemon=True).start()

auto_load_saved_lock()

update_timer()

root.mainloop()