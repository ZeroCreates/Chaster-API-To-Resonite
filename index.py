import os
import requests
import time
from flask import Flask
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("CHASTER_TOKEN")

app = Flask(__name__)

# cache
cached_end_date = None
last_fetch = 0
CACHE_TIME = 30  # seconds


def fetch_end_date():
    global cached_end_date, last_fetch

    if time.time() - last_fetch < CACHE_TIME:
        return cached_end_date

    url = "https://api.chaster.app/locks?status=active"

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    r = requests.get(url, headers=headers)
    locks = r.json()

    if not locks:
        cached_end_date = None
    else:
        cached_end_date = locks[0]["endDate"]

    last_fetch = time.time()

    return cached_end_date


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


@app.route("/timeleft")
def time_left():

    end_date = fetch_end_date()

    if not end_date:
        return "No active lock"

    return format_remaining(end_date)


if __name__ == "__main__":
    app.run(port=5000)