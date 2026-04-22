# Cyber Threat Intelligence Automator

An automated threat intelligence pipeline that pulls live malicious URLs, botnet 
command and control servers, and malware indicators from three free public threat 
feeds, saves them to a structured file, and sends Discord alerts   all running 
for free on GitHub Actions every 3 hours.

  What It Does
- Pulls live threat data from URLhaus, FeodoTracker, and ThreatFox every 3 hours
- Saves tens of thousands of active threats to a structured CSV file
- Breaks down threats by source and top malware families
- Sends a Discord alert every time new threats are collected
- Runs automatically on GitHub's servers   no manual work needed

  How It Works
1. GitHub Actions triggers the script on a schedule every 3 hours
2. `fetch_threats.py` fetches the latest threat feeds from all three sources
3. Results are cleaned, filtered, and saved to `threats.csv` in the repository
4. A Discord notification is sent with a full summary of findings

  File Breakdown

**`fetch_threats.py`**
This is the brain of the entire project. It installs its own dependencies, pulls 
from three live threat feeds, parses and cleans the raw data, filters for active 
threats only, saves everything to a CSV, and fires off a Discord alert with a 
breakdown of findings by source and malware family.

**`threats.csv`**
The output file where all collected threat data lives. It has seven columns   
source, id, date added, url, status, threat type, and malware family. It gets 
completely overwritten with fresh data every 3 hours and every update is saved 
in git history.

**`.github/workflows/run_cti.yml`**
The automation file that makes everything hands-free. It sets up a clean Ubuntu 
environment, installs Python, runs the script on a cron schedule, then commits 
and pushes the updated threats file back to the repository automatically.

**`README.md`**
Documents the entire project   what it does, how it works, the problems faced 
during development, and a full walkthrough of the code.

  Threat Feed Sources
- [URLhaus by Abuse.ch](https://urlhaus.abuse.ch)   malicious URLs used for malware distribution
- [FeodoTracker by Abuse.ch](https://feodotracker.abuse.ch)   botnet command and control servers
- [ThreatFox by Abuse.ch](https://threatfox.abuse.ch)   malware indicators including IPs, domains, and URLs

  Setup
1. Fork this repository
2. Create a Discord webhook and add it as a repository secret named `DISCORD_WEBHOOK`
3. Go to Settings → Actions → General → enable Read and write permissions
4. Run the workflow manually from the Actions tab to test

  Tech Stack
- Python
- GitHub Actions
- URLhaus, FeodoTracker, and ThreatFox APIs
- Discord Webhooks

 

  Code Walkthrough

The first thing the script does is install the `requests` library on its own 
using `subprocess`. Think of `requests` as Python's way of opening a browser 
and downloading something from the internet. By installing it inside the script 
we never have to worry about it being missing on whatever machine runs the code.

After that the imports load in. `requests` handles downloading the threat feeds. 
`csv` handles saving the results to a file. `os` is used to grab the Discord 
webhook URL from GitHub's secret storage so it never gets written directly into 
the code. `datetime` is used to stamp each run with the current date and time.

Next the script creates an empty list called `threats`. This is the bucket that 
all collected data gets dropped into before anything gets saved.

The script then hits the first feed, URLhaus. It downloads a live CSV of recent 
malicious URLs from Abuse.ch and loops through every line. Lines starting with 
`#` are comments so those get skipped. Each remaining line gets split by comma 
to separate the fields, and `.strip('"')` is used to clean off the extra 
quotation marks that come with the raw data. Only threats where 
`status == "online"` get kept   anything offline gets ignored since it's no 
longer an active danger.

The second feed is FeodoTracker which tracks botnet command and control servers. 
These are the secret addresses that malware uses to phone home to the hacker who 
deployed it. The same parsing approach applies and every entry gets labeled 
`botnet_c2` as its threat type.

The third feed is ThreatFox which covers a wider range of indicators including 
malicious IPs, domains, and URLs tied to known malware families. Again   split 
by comma, strip the quotes, add to the threats list.

Once all three feeds are pulled the script saves everything to `threats.csv` 
using `csv.DictWriter`. This is a CSV writer that works with dictionaries, 
meaning each row is written by column name rather than by position. That keeps 
the output clean and easy to read in any spreadsheet tool.

After saving, the script counts how many threats came from each source and which 
malware families appeared most often. It sorts by count and grabs the top 5 
families to include in the alert.

Finally the script grabs the Discord webhook URL using 
`os.environ.get("DISCORD_WEBHOOK")` and builds a message using an f-string   a 
Python feature that lets you drop live variables directly into text using curly 
braces. The message includes the total threat count, the timestamp, a per-source 
breakdown, and the top 5 malware families. It fires that off to Discord using 
`requests.post()` and the run is complete.

The whole thing takes about 30 seconds, collects tens of thousands of active 
threats from three real intelligence sources, saves them to your repo, and sends 
you a full summary on Discord   every 3 hours, automatically.

 

  Difficulties Faced and How We Solved Them

**The requirements.txt problem**
The biggest issue during development was `requirements.txt`. GitHub kept throwing 
the error `Could not open requirements file: No such file or directory` even after 
the file was created correctly and the workflow was updated multiple times. No 
matter what was tried   recreating the file, updating the workflow, clearing cache 
  GitHub kept referencing an old version. The fix was to remove `requirements.txt` 
completely and instead install the `requests` library directly inside the Python 
script itself using `subprocess.call(['pip', 'install', 'requests'])`. This 
bypassed the problem entirely and made the project more self-contained.

**GitHub Actions caching old workflow versions**
Even after editing `run_cti.yml`, the Actions runner kept executing the previous 
version of the file. This was fixed by rewriting the workflow file from scratch 
with simplified syntax and updated action versions   switching from 
`actions/checkout@v3` to `v4` and `setup-python@v4` to `v5`.

**Permission error when pushing results**
After the script successfully ran and generated over 25,000 threats, GitHub blocked 
the bot from pushing `threats.csv` back to the repository with a 403 permission 
error. The fix was going into repository Settings → Actions → General → Workflow 
permissions and enabling Read and write permissions.

**Python indentation error**
Python is extremely strict about indentation   every block of code needs to line 
up perfectly or the script crashes. An extra space before an `if` statement caused 
the script to fail. Fixing it was as simple as removing that one extra space, but 
it highlighted how important clean formatting is in Python.

**Updating the cron schedule**
The original schedule ran every 6 hours using `0 */6 * * *`. This was later 
updated to run every 3 hours by changing it to `0 */3 * * *`. Cron expressions 
use 5 fields representing minute, hour, day, month, and day of week   a small 
change with a big impact on how frequently the automator runs.

 

