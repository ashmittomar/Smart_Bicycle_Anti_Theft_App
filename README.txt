# Smart Bicycle Anti-Theft App

A simple Python Flask dashboard for the bicycle project.

## Three user options

1. Cycle Lock
2. Battery Percentage
3. GPS Location

The SMS alert is automatic. It is NOT a fourth user option.

## 1. Install Python

Use Python 3.10+.

## 2. Open terminal in this folder

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Run the app

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## Hardware integration

The hardware team can send HTTP POST requests to these routes:

### Lock
POST `/api/lock`

POST `/api/unlock`

### Battery

POST `/api/battery`

JSON:
```json
{"battery": 75}
```

### GPS

POST `/api/gps`

JSON:
```json
{"latitude": 28.6139, "longitude": 77.2090}
```

### Bicycle started

POST `/api/cycle-started`

This updates the dashboard and triggers the SMS function.

## SMS

The code uses Twilio for real SMS.

Set these environment variables before running:

Windows CMD:

```cmd
set TWILIO_SID=your_sid
set TWILIO_TOKEN=your_token
set TWILIO_FROM=your_twilio_number
set OWNER_PHONE=your_mobile_number
python app.py
```

If the Twilio values are not configured, the application runs in TEST MODE and prints the SMS in the terminal instead of sending a real SMS.

## Important hardware note

The Python application does not directly control the physical lock, read the physical battery, or read GPS by itself.

The hardware/microcontroller should send the current lock state, battery percentage and GPS coordinates to the Flask API.

For the final prototype, the hardware team can use an ESP32 or another suitable microcontroller and wireless communication module. The project synopsis already describes a microcontroller, GPS module, wireless communication module, battery and motion sensor architecture.
