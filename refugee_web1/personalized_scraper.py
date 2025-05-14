import requests
from bs4 import BeautifulSoup
from ml_filter import is_relevant
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# Define target websites
WEBSITES = {
    "https://www.unhcr.org": "UNHCR",
    "https://www.rescue.org": "IRC",
    "https://www.tent.org": "Tent",
    "https://refugees.org": "Refugees International",
    "https://www.opportunitiesforrefugees.org": "Opportunities for Refugees",
    "https://help.rescue.org": "IRC Help",
    "https://www.upwardlyglobal.org": "Upwardly Global",
    "https://rcusa.org/for-refugees/": "RCUSA",
    "https://www.refugeeemployment.org/": "Refugee Employment"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_opportunities(preferences):
    print("🧠 Scraping and filtering with ML model...")
    categorized = {}

    for url, label in WEBSITES.items():
        print(f"🔍 Scraping {url}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            links = soup.find_all("a", href=True)
            for link in links:
                text = link.get_text(strip=True)
                href = link['href']
                full_link = href if href.startswith("http") else url + href

                combined = f"{text} {full_link}"
                if any(pref in combined.lower() for pref in preferences):
                    if is_relevant(combined):
                        category = label
                        if category not in categorized:
                            categorized[category] = []
                        if combined not in categorized[category]:
                            categorized[category].append(f"- {text}\n  {full_link}")

        except Exception as e:
            print(f"❌ Failed to access {url}: {e}")

    return categorized

def send_opportunity_email(email, categorized):
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    if not categorized:
        body = "We couldn't find any new relevant opportunities today, but we'll keep checking."
    else:
        body = "Here are your latest refugee-related opportunities, filtered by relevance:\n\n"
        for site, items in categorized.items():
            body += f"--- {site} ---\n"
            body += "\n".join(items)
            body += "\n\n"
        body += "\nStay hopeful — we'll keep looking!"

    msg = MIMEText(body)
    msg["Subject"] = "Your Refugee Opportunities Update"
    msg["From"] = from_email
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
            print(f"✅ Opportunity email sent to {email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def run_scraper_for_user(user):
    print(f"🚀 Running direct scraper for {user['first_name']} ({user['email']})")
    categorized = scrape_opportunities(user["preferences"])
    send_opportunity_email(user["email"], categorized)

# Example use
if __name__ == "__main__":
    test_user = {
        "first_name": "Test",
        "email": "your@email.com",
        "preferences": ["scholarships", "jobs", "online courses"]
    }
    run_scraper_for_user(test_user)
