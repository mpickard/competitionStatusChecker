import subprocess
from bs4 import BeautifulSoup
import os
import sys

# -------------------------------
# Config
# -------------------------------

competitionNames = {
    "2025 OAK Brad Townsend Fall Classic": False,
    "Gus Ryder Memorial Cup 2025": False,
    "MAC Jingle Bell": False,
    "David Lawson Invitational 2026": False,
    "Jeff and Sandy Lee Invitational": False,
}

# Telegram bot details (stored in GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID environment variables")
    sys.exit(1)

# -------------------------------
# Helpers
# -------------------------------

def send_telegram_message(message: str):
    """Send a message via Telegram bot"""
    print(f"Sending telegram alert: {message}")
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        resp = requests.post(url, data=data)
        resp.raise_for_status()
        print(f"✅ Sent Telegram alert: {message}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")


def fetch_html(url: str) -> str:
    """Fetch HTML using curl via subprocess"""
    curl_command = [
        "curl",
        "-s",  # silent
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/115.0 Safari/537.36",
        url
    ]
    result = subprocess.run(curl_command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Curl command failed: {result.stderr}")
        sys.exit(1)
    return result.stdout


def check_competitions():
    """Fetch the swim meet page and look for competitions"""
    url = "https://www.swimming.ca/events-results-hub/upcoming-meets/"
    print(f"Fetching {url} ...")
    html = fetch_html(url)
    print(f"Fetched! \n {html}")

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")
    print(f"rows: {len(rows)}")

    for row in rows:
        cells = row.find_all("td", class_="tc")
        if len(cells) < 8:
            continue  # not a valid competition row

        comp_name = cells[1].get_text(strip=True)
        status = cells[6].get_text(strip=True)
        deadline = cells[7].get_text(strip=True)
        print(f"Comp_name: {comp_name},  Status: {status}")

        for target in competitionNames.keys():
            if target.lower() in comp_name.lower():
                print(f"Found '{comp_name}' → Status: {status}")
                if status.lower() == "active":
                    msg = (f"🏊 Attention! The following competition is now ready for entry:\n"
                           f"➡️ {comp_name}\n"
                           f"📅 Deadline for entries: {deadline}")
                    send_telegram_message(msg)
                else:
                    print(f"Competition {target} is not ready.")


if __name__ == "__main__":
    check_competitions()
