import firebase_admin
from firebase_admin import credentials, db

try:
    print("🔍 Loading Firebase key...")
    cred = credentials.Certificate("firebase_key.json")

    print("⚙️ Initializing Firebase app...")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://refugee-4506b-default-rtdb.firebaseio.com"
    })

    print("📡 Connecting to Firebase Realtime Database...")
    ref = db.reference("test")
    result = ref.push({"status": "working locally"})

    print("✅ Successfully pushed to Firebase! Key:", result.key)

except Exception as e:
    print("❌ ERROR:", e)
