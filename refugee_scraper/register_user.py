import json

def register_user():
    user = {}

    print("Welcome! Let's register your information.")

    user["first_name"] = input("First name: ").strip()
    user["last_name"] = input("Last name: ").strip()
    user["email"] = input("Email address (for notifications): ").strip()
    user["country"] = input("Country: ").strip()
    user["phone"] = input("Phone number: ").strip()
    user["address"] = input("Address: ").strip()

    print("\nWhat kind of opportunities are you looking for?")
    print("Options: scholarships, jobs, online courses, internships")
    preferences = input("Enter as comma-separated values: ").strip()
    user["preferences"] = [x.strip().lower() for x in preferences.split(",")]

    print("\nHow often would you like to receive updates?")
    print("Options: daily, weekly, monthly")
    user["frequency"] = input("Your choice: ").strip().lower()

    # Save user info to a file (append mode)
    with open("users.json", "a") as file:
        file.write(json.dumps(user) + "\n")

    print("\nThank you! You’ve been registered.")

if __name__ == "__main__":
    register_user()
pk
