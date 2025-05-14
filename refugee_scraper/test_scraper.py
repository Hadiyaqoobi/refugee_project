import requests

API_KEY = "AIzaSyB7_pHYGO0HflL11YcXe9GqZdkV9igZeFI"
SEARCH_ENGINE_ID = "3729371c581214e47"  # Replace this too
query = "scholarships for refugees 2025"

url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"

response = requests.get(url)
results = response.json()

for item in results.get("items", []):
    print(item["title"])
    print(item["link"])
    print()
