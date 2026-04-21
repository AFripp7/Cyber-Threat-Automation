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
    if len(parts) >= 8:
        id         = parts[0].strip('"')
        date_added = parts[1].strip('"')
        threat_url = parts[2].strip('"')
        status     = parts[3].strip('"')
        threat_type   = parts[5].strip('"')
        malware_family = parts[6].strip('"')

        if status == "online":
            threats.append({
                "id": id,
                "date_added": date_added,
                "url": threat_url,
                "status": status,
                "threat_type": threat_type,
                "malware_family": malware_family
            })


with open("threats.csv", "w", newline="") as f:
    writer =  csv.DictWriter(f, fieldnames=["id", "date_added", "url", "status", "threat_type", "malware_family"])
    writer.writeheader()
    for t in threats:
        writer.writerow(t)


families = {}
for t in threats:
    family = t["malware_family"] if t["malware_family"] != "None" else "Unknown"
    families[family] = families.get(family, 0) + 1

top_families = sorted(families.items(), key=lambda x: x[1], reverse=True)[:5]


print(f"Done! Found {len(threats)} active threats.")
print("Top malware families:", top_families)


# Send Discord alert
webhook_url = os.environ.get("DISCORD_WEBHOOK")
if webhook_url:
    family_lines = "\n".join([f"• {f}: {c} threats" for f, c in top_families])
    message = {
        "content": f"🚨 **CTI Automator Update**\n✅ **{len(threats)} active threats** found\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n**Top Malware Families:**\n{family_lines}"
    }
    requests.post(webhook_url, json=message)
    print("Discord alert sent!")
