from flask import Flask, render_template, request, redirect, url_for
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from db import init_db, save_user
from personalized_scraper import run_scraper_for_user, WEBSITES, scrape_website

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
init_db()  # Ensure SQLite table is ready

# Send a confirmation email
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
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

# Homepage
@app.route("/")
def home():
    return render_template("index.html")

# Registration Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            user = {
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "email": request.form["email"],
                "country": request.form["country"],
                "phone": request.form["phone"],
                "address": request.form["address"],
                "preferences": request.form.getlist("preferences"),
                "frequency": request.form["frequency"].lower()
            }

            save_user(user)
            print("💾 User saved to SQLite")

            confirmation_body = f"""Hello {user['first_name']},

Thank you for registering for refugee opportunity updates.

We'll send you info about:
- {', '.join(user['preferences'])}
Frequency: {user['frequency'].capitalize()}

Best,
Refugee Opportunities Team
"""
            send_email(user["email"], "Your Refugee Opportunity Subscription", confirmation_body)

            run_scraper_for_user(user)

            return redirect(url_for("thank_you"))

        except Exception as e:
            print(f"❌ Registration error: {e}")
            return "An error occurred. Please try again later.", 500

    return render_template("register.html")

# Thank You Page
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

# New Page: Display Current Opportunities
@app.route("/opportunities")
def opportunities():
    results = []
    for site in WEBSITES:
        try:
            site_results = scrape_website(site)
            for title, link in site_results:
                results.append({
                    "title": title,
                    "link": link,
                    "source": site
                })
        except Exception as e:
            print(f"❌ Error scraping {site}: {e}")
            continue

    return render_template("opportunities.html", results=results)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
