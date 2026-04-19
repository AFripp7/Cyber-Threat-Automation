import subprocess
subprocess.call(['pip', 'install', 'requests'])

import requests
import csv
import os
from datetime import datetime

print("Fetching threat data...")

url = "https://urlhaus.abuse.ch/downloads/csv_recent/"
response = requests.get(url)

lines = response.text.splitlines()

threats = []
for line in lines:
    if line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) >= 3:
        threats.append(parts)

with open("threats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date_collected", "raw_data"])
    for t in threats:
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), t])

print(f"Done! Found {len(threats)} threats.")

# Send Discord alert
webhook_url = os.environ.get("DISCORD_WEBHOOK")
if webhook_url:
    message = {
        "content": f"🚨 **CTI Automator Update**\n✅ Successfully pulled **{len(threats)} threats** from URLhaus\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
    }
    requests.post(webhook_url, json=message)
    print("Discord alert sent!")
