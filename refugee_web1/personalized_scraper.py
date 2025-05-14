import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv
from ml_filter import is_relevant

load_dotenv()

WEBSITES = [
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

KEYWORD_FALLBACKS = [
    "refugee", "asylum", "apply", "application",
    "job", "employment", "training", "course",
    "education", "scholarship", "mentorship", "program"
]

def is_relevant_or_keyword(text):
    if is_relevant(text):
        return True
    text_lower = text.lower()
    return any(word in text_lower for word in KEYWORD_FALLBACKS)

def scrape_website(url):
    try:
        print(f"🔍 Scraping {url}...")
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        links = soup.find_all("a")
        results = []
        for link in links:
            text = link.get_text(strip=True)
            href = link.get("href")
            if href and text:
                full_link = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                combined = f"{text} {full_link}"
                if is_relevant_or_keyword(combined):
                    results.append((text, full_link))
        return results
    except Exception as e:
        print(f"❌ Failed to access {url}: {e}")
        return []

def scrape_duckduckgo(query):
    print(f"🔍 DuckDuckGo: {query}")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    results = []
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("a.result__a")
        for link in links[:10]:
            title = link.get_text(strip=True)
            href = link.get("href")
            combined = f"{title} {href}"
            if is_relevant_or_keyword(combined):
                results.append((title, href))
    except Exception as e:
        print(f"❌ DuckDuckGo error: {e}")
    return results

def scrape_bing(query):
    print(f"🔍 Bing: {query}")
    url = f"https://www.bing.com/search?q={query}"
    results = []
    try:
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.select("li.b_algo h2 a")
        for link in links[:10]:
            title = link.get_text(strip=True)
            href = link.get("href")
            combined = f"{title} {href}"
            if is_relevant_or_keyword(combined):
                results.append((title, href))
    except Exception as e:
        print(f"❌ Bing error: {e}")
    return results

def format_email(user_name, categorized_results):
    lines = [f"Hello {user_name},\n", "Here are refugee-related opportunities we found for you:\n"]
    if not categorized_results:
        lines.append("We couldn't find any relevant opportunities this time, but we'll keep looking!")
        return "\n".join(lines)

    for site, items in categorized_results.items():
        lines.append(f"--- {site} ---")
        for title, url in items:
            lines.append(f"- {title}\n  {url}")
        lines.append("")

    lines.append("Stay hopeful — we'll keep searching for you!")
    return "\n".join(lines)

def send_email(to_email, subject, body):
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(from_email, password)
            smtp.send_message(msg)
            print(f"✅ Opportunity email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def run_scraper_for_user(user):
    print(f"🚀 Running direct scraper for {user['first_name']} ({user['email']})")
    categorized_results = {}

    # Existing websites
    for site in WEBSITES:
        results = scrape_website(site)
        if results:
            categorized_results[site] = results

    # Search engines based on preferences
    for pref in user.get("preferences", []):
        q = f"refugee {pref} 2025"
        ddg_results = scrape_duckduckgo(q)
        bing_results = scrape_bing(q)
        if ddg_results:
            categorized_results[f"DuckDuckGo: {q}"] = ddg_results
        if bing_results:
            categorized_results[f"Bing: {q}"] = bing_results

    body = format_email(user["first_name"], categorized_results)
    send_email(user["email"], "Your Refugee Opportunity Updates", body)

# For manual testing
if __name__ == "__main__":
    test_user = {
        "first_name": "Niloofar",
        "email": "your@email.com",
        "preferences": ["scholarships", "jobs", "online courses"]
    }
    run_scraper_for_user(test_user)
