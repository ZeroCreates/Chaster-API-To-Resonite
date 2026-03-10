# Chaster Cyber Lock Timer

A cyber-styled desktop timer that connects to the **Chaster API** and displays the remaining lock time for an active lock.

The application provides a clean cyber-terminal interface, automatically remembers your configuration, and exposes a simple local API endpoint so other programs can request the remaining time.

---

# Features

• Cyber-styled desktop interface
• Automatically saves API token and selected lock
• Handles multiple active locks
• Displays keyholder username
• Handles hidden timers
• 30-second API caching to avoid rate limits
• Local API endpoint for automation
• Automatically restores configuration on startup

---

# Requirements

• Python 3.9 or newer

Python packages required:

* Flask
* requests
* python-dotenv

These are included in `requirements.txt`.

---

# Installation

1. Download or clone the project.

2. Install the dependencies:

```
pip install -r requirements.txt
```

Or simply run:

```
grabRequirements.bat
```

---

# Running the Application

Run the program with:

```
run.bat
```

The desktop interface will open automatically.

---

# First Time Setup

1. Enter your **Chaster API Token**
2. Click **Fetch Locks**
3. Select the lock you want to track
4. Click **Save Lock**

The application will save your configuration to `.env`.

On the next launch your token and lock will automatically reload.

---

# API Endpoint

The application also runs a small local API server.

Example request:

```
http://localhost:5000/timeleft
```

Example responses:

```
5d 11h 22m 03s
```

or if the timer is hidden:

```
hidden
```

This endpoint can be used by:

• bots
• dashboards
• scripts
• automation tools

---

# Project Structure

```
project/
│
├── app.py
├── requirements.txt
├── .env (will be missing till the app saves the lock)
├── run.bat
├── grabRequirements.bat
└── README.md
```

---

# Batch Scripts

## run.bat

Runs the application.

## grabRequirements.bat

Installs the required Python packages.

---


# License

Personal use project.
