Cyber Threat Intelligence Automator

An automated threat intelligence pipeline that pulls live malicious URLs from public threat feeds, saves them to a structured file, and sends Discord alerts — all running for free on GitHub Actions.

What it does
- Pulls live threat data from URLhaus (Abuse.ch) every 6 hours
- Saves 25,000+ malicious URLs to a structured CSV file
- Sends a Discord alert every time new threats are collected
- Runs automatically on GitHub's servers — no manual work needed

## How it works
1. GitHub Actions triggers the script on a schedule (every 6 hours)
2. `fetch_threats.py` fetches the latest threat feed from URLhaus
3. Results are saved to `threats.csv` in the repository
4. A Discord notification is sent with a summary of findings

## Files
- `fetch_threats.py` — main script that fetches and parses threat data
- `threats.csv` — output file containing collected threat indicators
- `.github/workflows/run_cti.yml` — GitHub Actions automation workflow

## Threat Feed Sources
- [URLhaus by Abuse.ch](https://urlhaus.abuse.ch) — malicious URLs used for malware distribution

## Setup
1. Fork this repository
2. Create a Discord webhook and add it as a repository secret named `DISCORD_WEBHOOK`
3. Go to Settings → Actions → General → enable Read and write permissions
4. Run the workflow manually from the Actions tab to test

## Tech Stack
- Python
- GitHub Actions
- URLhaus API
- Discord Webhooks

## Future Plans
- Filter threats by type and severity
- Build a visual dashboard
