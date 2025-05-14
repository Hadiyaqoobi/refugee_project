import os
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from collections import defaultdict
from urllib.parse import urlparse

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SITES = [
    "https://www.unhcr.org",
    "https://www.rescue.org",
    "https://www.tent.org",
    "https://refugees.org",
    "https://www.opportunitiesforrefugees.org",
    "https://help.rescue.org",
    "https://www.upwardlyglobal.org",
    "https://rcusa.org/for-refugees/",
    "https://www.refugeeemployment.org/",
]

# Categories and their keywords
CATEGORIES = {
    "Employment": ["job", "work", "employment", "career", "hire"],
    "Training": ["training", "skill", "coach"],
    "Scholarships": ["scholarship", "funding", "tuition", "grant"],
    "Courses": ["course", "online", "class", "learn"],
    "Support": ["support", "aid", "help", "service", "resource"]
}

def categorize(text):
    for category, keywords in CATEGORIES.items():
        if any(k in text.lower() for k in keywords):
            return category
    return "Other"

def scrape_site(url):
    print(f"🔍 Scraping {url}...")
    results = defaultdict(list)
    seen = set()

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to access {url} (Status: {response.status_code})")
            return results

        soup = BeautifulSoup(response.text, "html.parser")
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]

            if not text and not any(k in href.lower() for k in sum(CATEGORIES.values(), [])):
                continue

            full_url = href if href.startswith("http") else base + "/" + href.lstrip("/")
            if full_url in seen:
                continue
            seen.add(full_url)

            label = text if text else full_url
            category = categorize(text + " " + href)
            results[category].append((label, full_url))

    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")

    return results

def send_opportunity_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Opportunity email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send opportunity email: {e}")

def run_scraper_for_user(user):
    print(f"🚀 Running direct scraper for {user['first_name']} ({user['email']})")
    body = f"Hello {user['first_name']},\n\nHere are some newly found refugee-related opportunities just for you:\n\n"

    any_found = False
    for site in SITES:
        categorized_links = scrape_site(site)
        if not any(categorized_links.values()):
            continue

        any_found = True
        parsed = urlparse(site)
        domain = parsed.netloc.replace("www.", "")
        body += f"{'='*43}\n📍 {domain} ({site})\n{'-'*43}\n"

        for category in sorted(categorized_links.keys()):
            links = categorized_links[category]
            if not links:
                continue
            body += f"🗂️ {category}\n"
            for title, link in links[:5]:
                body += f"- {title}\n  → {link}\n"
            body += "\n"

    if not any_found:
        body += "We couldn't find matching opportunities this time, but we'll keep looking!\n\n"

    body += "Stay hopeful — we’ll keep sending you updates!\n\nWarm regards,\nRefugee Opportunities Team"

    send_opportunity_email(user["email"], "Your Refugee Opportunity Updates", body)

# For manual test
if __name__ == "__main__":
    test_user = {
        "first_name": "Hadi",
        "email": "hadiyaqoobi@gmail.com",  # Replace with your real email for test
        "preferences": ["jobs", "training", "scholarships"]
    }
    run_scraper_for_user(test_user)
