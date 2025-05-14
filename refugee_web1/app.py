from flask import Flask, render_template, request, redirect, url_for
import os
import json
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from db import init_db, save_user  # <-- SQLite DB functions

# Load .env for local dev
load_dotenv()

app = Flask(__name__)

# Initialize the SQLite database
init_db()

# Send confirmation email
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

@app.route("/")
def home():
    return redirect(url_for("register"))

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
                "preferences": [x.strip().lower() for x in request.form["preferences"].split(",")],
                "frequency": request.form["frequency"].lower()
            }

            # Save to SQLite instead of Firebase
            save_user(user)

            # Send confirmation email
            body = f"""Hello {user['first_name']},

Thank you for registering for refugee opportunity updates.

We'll send you info about:
- {', '.join(user['preferences'])}
Frequency: {user['frequency'].capitalize()}

Best,
Refugee Opportunities Team
"""
            send_email(user["email"], "Your Refugee Opportunity Subscription", body)

            return redirect(url_for("thank_you"))

        except Exception as e:
            print(f"❌ Registration error: {e}")
            return "An error occurred. Please try again later.", 500

    return render_template("register.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
