import os
import json
import requests
import smtplib
from dotenv import load_dotenv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("GOOGLE_CSE_ID")


def load_user_preferences():
    """Load all registered users from users.json"""
    with open("users.json", "r") as file:
        return [json.loads(line.strip()) for line in file]


def search_google(query):
    """Run a Google Custom Search API query"""
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    response = requests.get(url)
    return response.json().get("items", [])


def send_email(recipient, subject, body):
    """Send an email using Gmail SMTP"""
    email_user = os.getenv("EMAIL_ADDRESS")
    email_pass = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")


def main():
    users = load_user_preferences()
    current_year = datetime.now().year

    for user in users:
        try:
            first_name = user["first_name"]
            last_name = user["last_name"]
            email = user["email"]
            preferences = user["preferences"]

            print(f"\nSearching for {first_name} {last_name} ({preferences})...\n")

            body = f"Hello {first_name},\n\nHere are some new opportunities we found just for you:\n"

            for preference in preferences:
                query = f"refugee {preference} {current_year}"
                results = search_google(query)

                icon = {
                    "scholarships": "🎓",
                    "jobs": "💼",
                    "online courses": "🧑‍💻",
                    "internships": "📋"
                }.get(preference.lower(), "📌")

                section_title = f"{icon} {preference.upper()} OPPORTUNITIES"
                body += f"\n{'=' * len(section_title)}\n{section_title}\n{'=' * len(section_title)}\n"

                valid_found = False

                for item in results[:10]:
                    title = item.get("title", "").strip()
                    snippet = item.get("snippet", "").strip()
                    link = item.get("link", "").strip()
                    full_text = f"{title} {snippet}".lower()

                    # Skip old content or summary/review-type results
                    if any(str(y) in full_text for y in range(2000, current_year)):
                        continue
                    if any(word in full_text for word in ["annual report", "celebrates", "review", "2020", "2021", "2022", "2023"]):
                        continue

                    body += f"\n• {title}\n  {snippet}\n  Learn more: {link}\n"
                    valid_found = True

                if not valid_found:
                    body += "Sorry, no new updates found right now.\n"

            body += "\n\nWe’ll continue sending you updates based on your interests.\nStay safe and take care!"

            send_email(email, "Your Refugee Opportunity Updates", body)

        except KeyError as e:
            print(f"❌ Skipping user due to missing field: {e}")
        except Exception as e:
            print(f"❌ Unexpected error with user {user.get('first_name', '?')} {user.get('last_name', '')}: {e}")


if __name__ == "__main__":
    main()
