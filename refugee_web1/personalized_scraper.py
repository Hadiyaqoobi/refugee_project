import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import os
from dotenv import load_dotenv

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

KEYWORDS = [
    "refugee", "asylum", "job", "employment", "work", "training", "course",
    "education", "scholarship", "mentorship", "apply", "application",
    "career", "certification", "bootcamp", "internship"
]

def is_keyword_match(text):
    return any(keyword in text.lower() for keyword in KEYWORDS)

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
                if is_keyword_match(text) or is_keyword_match(full_link):
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
            if is_keyword_match(title + " " + href):
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
            if is_keyword_match(title + " " + href):
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
    print(f"🚀 Running scraper for {user['first_name']} ({user['email']})")
    categorized_results = {}

    for site in WEBSITES:
        results = scrape_website(site)
        if results:
            categorized_results[site] = results

    for pref in user.get("preferences", []):
        query = f"refugee {pref} 2025"
        ddg_results = scrape_duckduckgo(query)
        bing_results = scrape_bing(query)
        if ddg_results:
            categorized_results[f"DuckDuckGo: {query}"] = ddg_results
        if bing_results:
            categorized_results[f"Bing: {query}"] = bing_results

    body = format_email(user["first_name"], categorized_results)
    send_email(user["email"], "Your Refugee Opportunity Updates", body)

# Optional test
if __name__ == "__main__":
    test_user = {
        "first_name": "Niloofar",
        "email": "your@email.com",
        "preferences": ["scholarship", "job", "online course"]
    }
    run_scraper_for_user(test_user)
