from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import run_engine

app = Flask(__name__)
CORS(app)

# ============================================
# API ROUTES
# ============================================

@app.route("/")
def home():
    return "Campaign IQ API is running — Engine v2 Active"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    raw_text = data.get("ads", "")

    # Panggil engine.py — semua logic di sana
    result = run_engine(raw_text)

    return jsonify(result)

@app.route("/join", methods=["POST"])
def join():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Email required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "Invalid email"}), 400

    with open("waitlist.txt", "a") as f:
        f.write(email + "\n")

    print(f"📧 New waitlist signup: {email}")

    return jsonify({"status": "success", "message": "Added to waitlist"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)