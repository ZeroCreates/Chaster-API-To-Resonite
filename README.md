# Chaster Lock Time API

A small API service that retrieves the remaining time from an active lock using the **Chaster API** and returns the remaining time as a formatted string.

The service caches the lock data to avoid excessive API requests and rate limits.

---

## Features

* Retrieves active lock information from Chaster
* Returns **remaining lock time as a formatted string**
* Built-in **30 second cache** to prevent API spam
* Simple **HTTP endpoint**
* Easy configuration using environment variables

---

## Requirements

* Python 3.9+
* A Chaster API token

Python packages required:

* Flask
* requests
* python-dotenv

---

## Installation

Clone or download the project and install the dependencies:

```
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project folder.

Example:

```
CHASTER_TOKEN=your_api_token_here
PORT=5000
```

### Environment Variables

| Variable      | Description                 |
| ------------- | --------------------------- |
| CHASTER_TOKEN | Your Chaster API token      |
| PORT          | Port the server will run on |

You can generate an API token from the **Chaster developer/API settings**.

---

## Running the Server

Start the server with:

```
python app.py
```

The server will start on the configured port (default: 5000).

Example:

```
http://localhost:5000
```

---

## API Endpoint

### Get Remaining Lock Time

```
GET /timeleft
```

Example request:

```
http://localhost:5000/timeleft
```

Example response:

```
6d 3h 18m 41s
```

The response is returned as a **plain string** containing the formatted time remaining on the active lock.

---

## Caching

To prevent hitting the Chaster API too frequently:

* Lock data is cached for **30 seconds**
* All requests during this period use the cached value
* The timer is calculated locally from the cached `endDate`

This significantly reduces API usage while keeping the timer accurate.

---

## Project Structure

```
project-folder/
│
├── app.py
├── requirements.txt
├── .env
└── README.md
```

---

## Example Use Cases

This API can be used for:

* Web dashboards
* Personal automation
* Server monitoring
* Bots or scripts that need the remaining lock time

---

## License

This project is provided as-is for personal use.
