import requests
import time
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MESSAGE = os.getenv("MESSAGE_TEXT")
INTERVAL = int(os.getenv("INTERVAL_SECONDS", 10))
AUTO_RESPONSE = os.getenv("AUTO_RESPONSE_TEXT")

API = "https://discord.com/api/v9"
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}

print("[SELF-BOT] Running...")
print(f"→ Sending every {INTERVAL}s to channel {CHANNEL_ID}")

last_dm = None

def send_message():
    r = requests.post(
        f"{API}/channels/{CHANNEL_ID}/messages",
        headers=HEADERS,
        json={"content": MESSAGE}
    )
    print("Message:", r.status_code)

def get_self():
    u = requests.get(f"{API}/users/@me", headers=HEADERS)
    if u.status_code != 200:
        return None
    return u.json()["id"]

SELF_ID = get_self()

def auto_reply():
    global last_dm
    r = requests.get(f"{API}/users/@me/channels", headers=HEADERS)
    if r.status_code != 200:
        return

    for dm in r.json():
        dm_id = dm["id"]
        msgs = requests.get(f"{API}/channels/{dm_id}/messages", headers=HEADERS).json()
        latest = msgs[0]

        if latest["author"]["id"] != SELF_ID and latest["id"] != last_dm:
            print("Replying to DM…")
            requests.post(
                f"{API}/channels/{dm_id}/messages",
                headers=HEADERS,
                json={"content": AUTO_RESPONSE}
            )
            last_dm = latest["id"]

while True:
    send_message()
    auto_reply()
    time.sleep(INTERVAL)
