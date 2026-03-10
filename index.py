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

# --- API CACHE ---
cached_end_date = None
last_fetch = 0
CACHE_TIME = 30

app = Flask(__name__)

# --- COLORS (Cyber theme) ---
BG = "#0a0a0a"
PANEL = "#111111"
CYAN = "#00ffff"
GREEN = "#00ff9c"
TEXT = "#e0e0e0"

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

            option = f"{lock['_id']} | {lock['endDate']}"
            options.append(option)

            if lock["_id"] == saved_lock:
                selected_index = i

        lock_dropdown["values"] = options

        if selected_index is not None:
            lock_dropdown.current(selected_index)

    except:
        pass
def format_remaining(end_date):

    if end_date == "HIDDEN":
        return "TIMER HIDDEN"

    end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    remaining = end - now
    seconds = int(remaining.total_seconds())

    if seconds < 0:
        return "UNLOCKED"

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

    data = r.json()

    # Hidden timer
    if data.get("endDate") is None:
        cached_end_date = "HIDDEN"
    else:
        cached_end_date = data["endDate"]

    last_fetch = time.time()

    return cached_end_date


# --- API SERVER ---
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


# --- GUI ---
root = tk.Tk()
root.title("Chaster Cyber Timer")
root.geometry("500x420")
root.configure(bg=BG)

locks = []


# Title
title = tk.Label(
    root,
    text="CHASTER LOCK TIMER",
    bg=BG,
    fg=CYAN,
    font=("Consolas", 18, "bold")
)

title.pack(pady=10)


# Token Input
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
    width=45,
    bg=PANEL,
    fg=GREEN,
    insertbackground=GREEN,
    font=("Consolas", 10),
    relief="flat"
)

token_entry.pack(pady=5)


# Dropdown
lock_dropdown = ttk.Combobox(root, width=50)
lock_dropdown.pack(pady=10)


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

    if not token:
        return

    selected = lock_dropdown.current()

    if selected < 0:
        return

    lock_id = locks[selected]["_id"]

    set_key(ENV_FILE, "CHASTER_TOKEN", token)
    set_key(ENV_FILE, "LOCK_ID", lock_id)


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


# Timer display
timer_label = tk.Label(
    root,
    text="NOT CONFIGURED",
    bg=BG,
    fg=GREEN,
    font=("Consolas", 28, "bold")
)

timer_label.pack(pady=40)


def update_timer():

    token = os.getenv("CHASTER_TOKEN")
    lock_id = os.getenv("LOCK_ID")

    if token and lock_id:
        end_date = fetch_end_date(token, lock_id)
        remaining = format_remaining(end_date)
        timer_label.config(text=remaining)

    root.after(1000, update_timer)


# Start API in background
threading.Thread(target=start_api, daemon=True).start()

auto_load_saved_lock()

update_timer()

root.mainloop()