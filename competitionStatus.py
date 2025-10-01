import time
import requests
from bs4 import BeautifulSoup

# 1. Competitions to track
competitionNames = {
    "2025 OAK Brad Townsend Fall Classic": False,
    "Gus Ryder Memorial Cup 2025": False,
    "MAC Jingle Bell": False,
    "David Lawson Invitational 2026": False,
    "Jeff and Sandy Lee Invitational": False,

}

# --- Telegram Settings ---
TELEGRAM_TOKEN = "8365791407:AAFa-ToaqczcvaAxVqLeAUl93E7NSD_wxnE"   # from BotFather
CHAT_ID = "8308952773"            # from https://api.telegram.org/bot8365791407:AAFa-ToaqczcvaAxVqLeAUl93E7NSD_wxnE/getUpdates

def send_telegram(message: str):
    """Send a Telegram message via bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
        print(f"[INFO] Sent Telegram alert: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

# --- Competition Check ---
def check_competitions():
    """Fetch the webpage and check competitions for readiness."""
    url = "https://www.swimming.ca/events-results-hub/upcoming-meets/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 8:
            continue

        comp_name = cells[1].get_text(strip=True)
        status = cells[6].get_text(strip=True).lower()
        deadline = cells[7].get_text(strip=True)

        # Look for a tracked competition
        for target in competitionNames.keys():
            if competitionNames[target]:
                continue  # already marked ready
            if target.lower() in comp_name.lower():
                if status == "active":
                    # Send Telegram alert
                    message = (
                        f"🚨 Competition Ready 🚨\n\n"
                        f"{target} is now ready for entry!\n"
                        f"Deadline: {deadline}"
                    )
                    send_telegram(message)

                    # Mark ready
                    competitionNames[target] = True
                    print(f"[INFO] Marked {target} as ready.")

    return all(competitionNames.values())

# --- Main Loop ---
if __name__ == "__main__":
    while True:
        try:
            print("[INFO] Checking competitions...")
            all_ready = check_competitions()
            if all_ready:
                print("[INFO] All competitions are ready. Exiting.")
                break
        except Exception as e:
            print(f"[ERROR] {e}")

        print("[INFO] Sleeping for 1 hour...")
        time.sleep(3600)
