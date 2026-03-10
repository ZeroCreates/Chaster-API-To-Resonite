==============================
Resonite X Chaster Timer
==============================

A cyber-styled desktop app for tracking your active Chaster locks. 
This app shows remaining lock time, keyholder information, and lets 
you add time remotely via a local API.  

It’s fully packaged as a .exe — users do NOT need Python or any dependencies. 
The .exe automatically creates a .env file on first run.  

--------------------------------
Features
--------------------------------
- Cyber-terminal styled GUI
- Shows remaining lock time, updates every second
- Handles hidden timers gracefully
- Displays keyholder username
- Auto-saves API token and lock ID in .env
- Auto-restores settings on reopen
- POST endpoint to add time to a lock (default +1 hour)
- Local /timeleft API for external use
- Fully self-contained .exe — no Python install required

--------------------------------
Requirements
--------------------------------
- Windows 10 or higher
- Lock must be VISIBLE to see the remaining time
- Nothing else — the .exe is fully portable

--------------------------------
First Time Setup
--------------------------------
1. Run Resonite X Chaster Timer.exe
2. Enter your Chaster API Token
3. Click "Fetch Locks"
4. Select your lock from the dropdown
5. Click "Save Lock"

- The .env file is created automatically in the same folder as the .exe
- On subsequent runs, your token and lock are restored automatically

--------------------------------
Local API Usage
--------------------------------
GET Remaining Time:
http://localhost:5000/timeleft
Example response:
5d 12h 03m 21s
or if the timer is hidden:
hidden

POST Add Time to Lock:
http://localhost:5000/addtime
Content-Type: application/json

{
  "seconds": 3600
}

- Adds 1 hour (3600 seconds) to the lock
- Returns:
{
  "status": "success",
  "added_seconds": 3600
}

--------------------------------
Folder
--------------------------------
Resonite Folder Path: [Insert your Resonite folder path here]

--------------------------------
Notes
--------------------------------
- .env can be manually edited if needed
- Firewall may ask to allow the app to use port 5000 (for the local API)
- Hidden timers show as "TIMER HIDDEN" in the GUI and "hidden" via API
- Lock must be visible to see remaining time