import requests
import time
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MESSAGE = os.getenv("MESSAGE_TEXT")
INTERVAL = int(os.getenv("INTERVAL_SECONDS", 10))
AUTO_RESPONSE = os.getenv("AUTO_RESPONSE_TEXT")

API = "https://discord.com/api/v9"

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

print("[SELF-BOT] Started!")
print(f"> Sending every {INTERVAL}s → Channel {CHANNEL_ID}")

last_dm = None
SELF_ID = None

def get_self_id():
    global SELF_ID
    if SELF_ID:
        return SELF_ID

    r = requests.get(f"{API}/users/@me", headers=HEADERS)
    if r.status_code != 200:
        print("!! FAILED GET SELF ID:", r.status_code, r.text)
        return None
    SELF_ID = r.json()["id"]
    return SELF_ID

def send_message():
    data = {"content": MESSAGE}
    r = requests.post(f"{API}/channels/{CHANNEL_ID}/messages", headers=HEADERS, data=json.dumps(data))
    print(f"[SEND] Status: {r.status_code}, Response: {r.text}")
    if r.status_code == 429:
        delay = r.json().get("retry_after", 5)
        print(f"!! RATE LIMITED — waiting {delay}s")
        time.sleep(delay)
    elif r.status_code != 200:
        print(f"!! SEND FAILED: {r.status_code} - {r.text}")

def check_dm():
    global last_dm
    r = requests.get(f"{API}/users/@me/channels", headers=HEADERS)
    if r.status_code != 200:
        print(f"[DM CHANNELS ERR] {r.status_code}: {r.text}")
        return
    for dm in r.json():
        dm_id = dm["id"]
        msgs = requests.get(f"{API}/channels/{dm_id}/messages", headers=HEADERS)
        if msgs.status_code != 200:
            continue
        latest = msgs.json()[0]
        if latest["author"]["id"] != get_self_id() and latest["id"] != last_dm:
            print(f"Replying to DM: {latest['content']}")
            reply_r = requests.post(f"{API}/channels/{dm_id}/messages", headers=HEADERS, data=json.dumps({"content": AUTO_RESPONSE}))
            print(f"[DM REPLY] Status: {reply_r.status_code}, Response: {reply_r.text}")
            last_dm = latest["id"]

# MAIN LOOP
while True:
    try:
        send_message()
        check_dm()
    except Exception as e:
        print("!! ERROR:", e)

    time.sleep(INTERVAL)
