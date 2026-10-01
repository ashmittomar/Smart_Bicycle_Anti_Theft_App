import os
import webbrowser
from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
from twilio.rest import Client


# ============================================================
# LOAD .ENV FILE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OWNER_PHONE_NUMBER = os.getenv("OWNER_PHONE_NUMBER")


# ============================================================
# APPLICATION SETTINGS
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_BG = "#0F172A"
CARD_BG = "#1E293B"

TEXT = "#F8FAFC"
MUTED = "#94A3B8"

GREEN = "#22C55E"
RED = "#EF4444"
BLUE = "#3B82F6"
YELLOW = "#F59E0B"


# ============================================================
# MAIN WINDOW
# ============================================================

app = ctk.CTk()

app.title("Smart Bicycle - Anti-Theft & GPS Alert System")

app.geometry("920x700")
app.minsize(850, 650)

app.configure(fg_color=APP_BG)


# ============================================================
# SYSTEM DATA
# ============================================================

cycle_locked = True

battery = 80

# Demo GPS coordinates
# These can later be replaced by real GPS data
latitude = 28.6139
longitude = 77.2090

alert_active = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def current_time():
    return datetime.now().strftime("%H:%M:%S")


def update_activity(text):
    activity_label.configure(text=text)


def open_google_maps():

    url = f"https://www.google.com/maps?q={latitude},{longitude}"

    webbrowser.open(url)


def sms_configuration_ready():

    values = [
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
        OWNER_PHONE_NUMBER
    ]

    return all(values)


# ============================================================
# SEND SMS
# ============================================================

def send_sms_alert():

    if not TWILIO_ACCOUNT_SID:
        return False, "Twilio Account SID is missing."

    if not TWILIO_AUTH_TOKEN:
        return False, "Twilio Auth Token is missing."

    if not TWILIO_PHONE_NUMBER:
        return False, "Twilio phone number is missing."

    if not OWNER_PHONE_NUMBER:
        return False, "Owner phone number is missing."

    try:

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        # Twilio Trial accounts require
        # predefined SMS templates.
        message = client.messages.create(
            body="sms_internal_alerts",
            from_=TWILIO_PHONE_NUMBER,
            to=OWNER_PHONE_NUMBER
        )

        return True, message.sid

    except Exception as error:

        return False, str(error)

# ============================================================
# LOCK / UNLOCK
# ============================================================

def lock_cycle():

    global cycle_locked
    global alert_active

    cycle_locked = True
    alert_active = False

    lock_status.configure(
        text="LOCKED",
        text_color=GREEN
    )

    lock_description.configure(
        text="Your bicycle is protected"
    )

    lock_icon.configure(
        text="🔒"
    )

    lock_button.configure(
        text="🔓  UNLOCK CYCLE",
        fg_color=BLUE,
        hover_color="#2563EB"
    )

    security_status.configure(
        text="🔒  BICYCLE SECURED",
        text_color=GREEN
    )

    gps_state.configure(
        text="GPS active",
        text_color=GREEN
    )

    update_activity(
        f"Cycle locked at {current_time()}"
    )


def unlock_cycle():

    global cycle_locked
    global alert_active

    answer = messagebox.askyesno(
        "Unlock Bicycle",
        "Are you sure you want to unlock the bicycle?"
    )

    if not answer:
        return

    cycle_locked = False
    alert_active = False

    lock_status.configure(
        text="UNLOCKED",
        text_color=YELLOW
    )

    lock_description.configure(
        text="Bicycle security is disabled"
    )

    lock_icon.configure(
        text="🔓"
    )

    lock_button.configure(
        text="🔒  LOCK CYCLE",
        fg_color="#16A34A",
        hover_color="#15803D"
    )

    security_status.configure(
        text="⚠  BICYCLE UNLOCKED",
        text_color=YELLOW
    )

    gps_state.configure(
        text="GPS standby",
        text_color=MUTED
    )

    update_activity(
        f"Cycle unlocked at {current_time()}"
    )


def toggle_lock():

    if cycle_locked:
        unlock_cycle()

    else:
        lock_cycle()


# ============================================================
# BATTERY
# ============================================================

def update_battery():

    battery_value.configure(
        text=f"{battery}%"
    )

    battery_bar.set(
        battery / 100
    )

    if battery <= 20:

        battery_value.configure(
            text_color=RED
        )

        battery_state.configure(
            text="LOW BATTERY",
            text_color=RED
        )

    elif battery <= 50:

        battery_value.configure(
            text_color=YELLOW
        )

        battery_state.configure(
            text="MEDIUM",
            text_color=YELLOW
        )

    else:

        battery_value.configure(
            text_color=GREEN
        )

        battery_state.configure(
            text="GOOD",
            text_color=GREEN
        )


def increase_battery():

    global battery

    battery = min(
        100,
        battery + 5
    )

    update_battery()


def decrease_battery():

    global battery

    battery = max(
        0,
        battery - 5
    )

    update_battery()


# ============================================================
# MOVEMENT TEST
# ============================================================

def test_movement():

    global alert_active

    # --------------------------------------------------------
    # IF BICYCLE IS UNLOCKED
    # --------------------------------------------------------

    if not cycle_locked:

        alert_active = False

        security_status.configure(
            text="✓  NORMAL MOVEMENT",
            text_color=GREEN
        )

        gps_state.configure(
            text="GPS standby",
            text_color=MUTED
        )

        update_activity(
            f"Normal movement detected at {current_time()}"
        )

        messagebox.showinfo(
            "Normal Movement",
            "The bicycle is currently unlocked.\n\n"
            "Movement detected, but no anti-theft SMS was sent."
        )

        return

    # --------------------------------------------------------
    # BICYCLE IS LOCKED
    # --------------------------------------------------------

    alert_active = True

    security_status.configure(
        text="🚨  UNAUTHORIZED MOVEMENT!",
        text_color=RED
    )

    gps_state.configure(
        text="GPS TRACKING ACTIVE",
        text_color=RED
    )

    update_activity(
        f"Movement detected at {current_time()}"
    )

    # --------------------------------------------------------
    # SEND SMS
    # --------------------------------------------------------

    success, result = send_sms_alert()

    if success:

        sms_status.configure(
            text="SMS: SENT",
            text_color=GREEN
        )

        messagebox.showwarning(
            "ANTI-THEFT ALERT",

            "Unauthorized bicycle movement detected!\n\n"
            "GPS tracking has been activated.\n\n"
            "✓ SMS SENT TO OWNER."
        )

    else:

        sms_status.configure(
            text="SMS: FAILED",
            text_color=RED
        )

        messagebox.showerror(
            "ANTI-THEFT ALERT",

            "Unauthorized bicycle movement detected!\n\n"
            "GPS tracking has been activated.\n\n"
            "✕ SMS COULD NOT BE SENT.\n\n"
            f"Error:\n{result}"
        )


# ============================================================
# RESET ALERT
# ============================================================

def reset_alert():

    global alert_active

    alert_active = False

    if cycle_locked:

        security_status.configure(
            text="🔒  BICYCLE SECURED",
            text_color=GREEN
        )

        gps_state.configure(
            text="GPS active",
            text_color=GREEN
        )

    else:

        security_status.configure(
            text="⚠  BICYCLE UNLOCKED",
            text_color=YELLOW
        )

        gps_state.configure(
            text="GPS standby",
            text_color=MUTED
        )

    if sms_configuration_ready():

        sms_status.configure(
            text="SMS: READY",
            text_color=GREEN
        )

    else:

        sms_status.configure(
            text="SMS: NOT CONFIGURED",
            text_color=YELLOW
        )

    update_activity(
        "Security alert reset"
    )


# ============================================================
# HEADER
# ============================================================

header = ctk.CTkFrame(
    app,
    fg_color=APP_BG,
    corner_radius=0
)

header.pack(
    fill="x",
    padx=30,
    pady=(22, 10)
)


# LEFT SIDE HEADER

header_left = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

header_left.pack(
    side="left"
)


title_label = ctk.CTkLabel(
    header_left,

    text="🚲  SMART BICYCLE",

    font=ctk.CTkFont(
        size=28,
        weight="bold"
    ),

    text_color=TEXT
)

title_label.pack(
    anchor="w"
)


subtitle_label = ctk.CTkLabel(
    header_left,

    text="Anti-Theft & GPS Alert System",

    font=ctk.CTkFont(
        size=14
    ),

    text_color=MUTED
)

subtitle_label.pack(
    anchor="w",
    pady=(3, 0)
)


# RIGHT SIDE HEADER

online_label = ctk.CTkLabel(
    header,

    text="●  SYSTEM ONLINE",

    font=ctk.CTkFont(
        size=14,
        weight="bold"
    ),

    text_color=GREEN
)

online_label.pack(
    side="right",
    pady=10
)


# ============================================================
# MAIN CONTENT
# ============================================================

content = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

content.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=10
)


content.grid_columnconfigure(
    0,
    weight=1
)

content.grid_columnconfigure(
    1,
    weight=1
)

content.grid_columnconfigure(
    2,
    weight=1
)

content.grid_rowconfigure(
    0,
    weight=1
)

content.grid_rowconfigure(
    1,
    weight=1
)


# ============================================================
# SECURITY CARD
# ============================================================

security_card = ctk.CTkFrame(
    content,
    fg_color=CARD_BG,
    corner_radius=18
)

security_card.grid(
    row=0,
    column=0,
    padx=(0, 8),
    pady=8,
    sticky="nsew"
)


ctk.CTkLabel(
    security_card,

    text="CYCLE SECURITY",

    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),

    text_color=MUTED
).pack(
    pady=(20, 8)
)


lock_icon = ctk.CTkLabel(
    security_card,

    text="🔒",

    font=ctk.CTkFont(
        size=48
    )
)

lock_icon.pack(
    pady=(5, 0)
)


lock_status = ctk.CTkLabel(
    security_card,

    text="LOCKED",

    font=ctk.CTkFont(
        size=24,
        weight="bold"
    ),

    text_color=GREEN
)

lock_status.pack(
    pady=(5, 0)
)


lock_description = ctk.CTkLabel(
    security_card,

    text="Your bicycle is protected",

    font=ctk.CTkFont(
        size=13
    ),

    text_color=MUTED
)

lock_description.pack(
    pady=(4, 14)
)


lock_button = ctk.CTkButton(
    security_card,

    text="🔓  UNLOCK CYCLE",

    height=44,

    corner_radius=10,

    font=ctk.CTkFont(
        size=14,
        weight="bold"
    ),

    fg_color=BLUE,

    hover_color="#2563EB",

    command=toggle_lock
)

lock_button.pack(
    fill="x",
    padx=20,
    pady=(0, 20)
)


# ============================================================
# BATTERY CARD
# ============================================================

battery_card = ctk.CTkFrame(
    content,
    fg_color=CARD_BG,
    corner_radius=18
)

battery_card.grid(
    row=0,
    column=1,
    padx=8,
    pady=8,
    sticky="nsew"
)


ctk.CTkLabel(
    battery_card,

    text="BATTERY",

    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),

    text_color=MUTED
).pack(
    pady=(20, 5)
)


battery_value = ctk.CTkLabel(
    battery_card,

    text="80%",

    font=ctk.CTkFont(
        size=32,
        weight="bold"
    ),

    text_color=GREEN
)

battery_value.pack()


battery_bar = ctk.CTkProgressBar(
    battery_card,

    height=14,

    corner_radius=7
)

battery_bar.pack(
    fill="x",
    padx=25,
    pady=(12, 6)
)


battery_state = ctk.CTkLabel(
    battery_card,

    text="GOOD",

    font=ctk.CTkFont(
        size=13,
        weight="bold"
    ),

    text_color=GREEN
)

battery_state.pack(
    pady=(0, 12)
)


battery_controls = ctk.CTkFrame(
    battery_card,

    fg_color="transparent"
)

battery_controls.pack(
    pady=(0, 18)
)





# ============================================================
# GPS CARD
# ============================================================

gps_card = ctk.CTkFrame(
    content,
    fg_color=CARD_BG,
    corner_radius=18
)

gps_card.grid(
    row=0,
    column=2,
    padx=(8, 0),
    pady=8,
    sticky="nsew"
)


ctk.CTkLabel(
    gps_card,

    text="GPS LOCATION",

    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),

    text_color=MUTED
).pack(
    pady=(20, 8)
)


coordinates = ctk.CTkLabel(
    gps_card,

    text=(
        f"LAT  {latitude:.4f}° N\n"
        f"LON  {longitude:.4f}° E"
    ),

    justify="left",

    font=ctk.CTkFont(
        size=14,
        weight="bold"
    ),

    text_color=TEXT
)

coordinates.pack(
    pady=5
)


gps_state = ctk.CTkLabel(
    gps_card,

    text="GPS active",

    font=ctk.CTkFont(
        size=13,
        weight="bold"
    ),

    text_color=GREEN
)

gps_state.pack(
    pady=(5, 2)
)


gps_update = ctk.CTkLabel(
    gps_card,

    text="Last update: Just now",

    font=ctk.CTkFont(
        size=12
    ),

    text_color=MUTED
)

gps_update.pack(
    pady=(0, 12)
)


ctk.CTkButton(
    gps_card,

    text="📍  OPEN GOOGLE MAPS",

    height=40,

    corner_radius=10,

    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),

    command=open_google_maps
).pack(
    fill="x",
    padx=18,
    pady=(0, 18)
)


# ============================================================
# SECURITY STATUS CARD
# ============================================================

status_card = ctk.CTkFrame(
    content,
    fg_color=CARD_BG,
    corner_radius=18
)

status_card.grid(
    row=1,
    column=0,
    columnspan=2,
    padx=(0, 8),
    pady=8,
    sticky="nsew"
)


ctk.CTkLabel(
    status_card,

    text="SECURITY STATUS",

    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),

    text_color=MUTED
).pack(
    anchor="w",
    padx=20,
    pady=(18, 5)
)


security_status = ctk.CTkLabel(
    status_card,

    text="🔒  BICYCLE SECURED",

    font=ctk.CTkFont(
        size=20,
        weight="bold"
    ),

    text_color=GREEN
)

security_status.pack(
    anchor="w",
    padx=20,
    pady=(0, 5)
)


activity_label = ctk.CTkLabel(
    status_card,

    text="Cycle locked and ready.",

    font=ctk.CTkFont(
        size=13
    ),

    text_color=MUTED
)

activity_label.pack(
    anchor="w",
    padx=20,
    pady=(0, 12)
)


sms_status = ctk.CTkLabel(
    status_card,

    text=(
        "SMS: READY"
        if sms_configuration_ready()
        else "SMS: NOT CONFIGURED"
    ),

    font=ctk.CTkFont(
        size=13,
        weight="bold"
    ),

    text_color=(
        GREEN
        if sms_configuration_ready()
        else YELLOW
    )
)

sms_status.pack(
    anchor="w",
    padx=20,
    pady=(0, 15)
)


# ============================================================
# TEST CARD
# ============================================================

action_card = ctk.CTkFrame(
    content,
    fg_color=CARD_BG,
    corner_radius=18
)

action_card.grid(
    row=1,
    column=2,
    padx=(8, 0),
    pady=8,
    sticky="nsew"
)


ctk.CTkLabel(
    action_card,

    text="ANTI-THEFT TEST",

    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),

    text_color=MUTED
).pack(
    pady=(18, 8)
)


ctk.CTkLabel(
    action_card,

    text=(
        "Simulate bicycle movement\n"
        "to test the security system."
    ),

    justify="center",

    font=ctk.CTkFont(
        size=12
    ),

    text_color=MUTED
).pack(
    pady=(0, 12)
)


ctk.CTkButton(
    action_card,

    text="⚠  TEST MOVEMENT ALERT",

    height=42,

    corner_radius=10,

    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),

    fg_color="#B91C1C",

    hover_color="#991B1B",

    command=test_movement
).pack(
    fill="x",
    padx=18,
    pady=5
)


ctk.CTkButton(
    action_card,

    text="↻  RESET ALERT",

    height=38,

    corner_radius=10,

    font=ctk.CTkFont(
        size=12,
        weight="bold"
    ),

    fg_color="#475569",

    hover_color="#334155",

    command=reset_alert
).pack(
    fill="x",
    padx=18,
    pady=(3, 15)
)


# ============================================================
# START APPLICATION
# ============================================================

update_battery()

app.mainloop()