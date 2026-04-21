import subprocess
subprocess.call(['pip', 'install', 'requests'])

import requests
import csv
import os
from datetime import datetime

print("Fetching threat data...")

threats = []

# Feed 1: URLhaus - malicious URLs
print("Pulling URLhaus feed...")
urlhaus_response = requests.get("https://urlhaus.abuse.ch/downloads/csv_recent/")
for line in urlhaus_response.text.splitlines():
    if line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) >= 8:
        status = parts[3].strip('"')
        if status == "online":
            threats.append({
                "source": "URLhaus",
                "id": parts[0].strip('"'),
                "date_added": parts[1].strip('"'),
                "url": parts[2].strip('"'),
                "status": status,
                "threat_type": parts[5].strip('"'),
                "malware_family": parts[6].strip('"')
            })

# Feed 2 botnet C2 servers
print("Pulling FeodoTracker feed...")
feodo_response = requests.get("https://feodotracker.abuse.ch/downloads/ipblocklist.csv")
for line in feodo_response.text.splitlines():
    if line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) >= 4:
        threats.append({
            "source": "FeodoTracker",
            "id": "",
            "date_added": parts[0].strip('"'),
            "url": parts[1].strip('"'),
            "status": "online",
            "threat_type": "botnet_c2",
            "malware_family": parts[3].strip('"')
        })

# Feed 3 malware IOCs
print("Pulling ThreatFox feed...")
threatfox_response = requests.get("https://threatfox.abuse.ch/export/csv/recent/")
for line in threatfox_response.text.splitlines():
    if line.startswith("#"):
        continue
    parts = line.split(",")
    if len(parts) >= 6:
        threats.append({
            "source": "ThreatFox",
            "id": parts[0].strip('"'),
            "date_added": parts[1].strip('"'),
            "url": parts[2].strip('"'),
            "status": "online",
            "threat_type": parts[3].strip('"'),
            "malware_family": parts[5].strip('"')
        })

# Save to CSV
print(f"Saving {len(threats)} total threats...")
with open("threats.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["source", "id", "date_added", "url", "status", "threat_type", "malware_family"])
    writer.writeheader()
    for t in threats:
        writer.writerow(t)

# Counts
sources = {}
for t in threats:
    sources[t["source"]] = sources.get(t["source"], 0) + 1

families = {}
for t in threats:
    family = t["malware_family"] if t["malware_family"] != "None" else "Unknown"
    families[family] = families.get(family, 0) + 1

top_families = sorted(families.items(), key=lambda x: x[1], reverse=True)[:5]

print(f"Done! Found {len(threats)} total threats.")
print("Sources:", sources)
print("Top malware families:", top_families)

# Send Discord alert
webhook_url = os.environ.get("DISCORD_WEBHOOK")
if webhook_url:
    source_lines = "\n".join([f"• {s}: {c} threats" for s, c in sources.items()])
    family_lines = "\n".join([f"• {f}: {c} threats" for f, c in top_families])
    message = {
        "content": f"🚨 **CTI Automator Update**\n✅ **{len(threats)} total threats** found\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n**Sources:**\n{source_lines}\n\n**Top Malware Families:**\n{family_lines}"
    }
    requests.post(webhook_url, json=message)
    print("Discord alert sent!")
