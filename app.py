from flask import Flask, request, jsonify, render_template, Response, send_from_directory
from flask_cors import CORS
from engine import run_engine
from dotenv import load_dotenv
load_dotenv()
from database_postgres import (
    init_db,
    save_analysis,
    get_history,
    get_history_by_user,
    create_user,
    verify_user,
    delete_analysis,
    delete_all_history
)

import csv
import io
import os
import psycopg2

app = Flask(__name__)
CORS(app)

# ============================================
# POSTGRESQL CONNECTION (GUNA DATABASE_URL)
# ============================================
def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])


# ============================================
# SERVE STATIC FILES (CSS, JS, etc.)
# ============================================
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# ============================================
# TEST ROUTE — SEMAK POSTGRES CONNECTION
# ============================================
@app.route("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        result = cur.fetchone()
        conn.close()
        return str(result)
    except Exception as e:
        return f"DB ERROR: {str(e)}"


# ============================================
# TEST ROUTE — JSON INPUT KE ENGINE
# ============================================
@app.route("/test-json")
def test_json():

    sample = {
        "campaigns": [
            {
                "name": "Facebook Ads",
                "budget": 100,
                "ctr": 2.1,
                "cpc": 0.80,
                "roas": 3.5,
                "conversions": 20
            }
        ]
    }

    return jsonify(run_engine(sample))


# ============================================
# INIT DB (PostgreSQL)
# ============================================
init_db()


# ============================================
# HOME (FRONTEND)
# ============================================
@app.route("/")
def home():
    return render_template("index.html")


# ============================================
# ANALYZE ENGINE
# ============================================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    raw_text = data.get("ads", "")
    user_id = data.get("user_id")

    result = run_engine(raw_text)

    # attach user
    result["user_id"] = user_id

    # save
    if user_id:
        save_analysis(user_id, result)
    else:
        save_analysis(None, result)

    return jsonify(result)


# ============================================
# REGISTER
# ============================================

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    full_name = data.get("full_name")
    company_name = data.get("company_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name:
        return jsonify({"error": "Full name required"}), 400

    if not company_name:
        return jsonify({"error": "Company name required"}), 400

    if not email:
        return jsonify({"error": "Email required"}), 400

    if not password:
        return jsonify({"error": "Password required"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if "@" not in email:
        return jsonify({
            "error": "Invalid email"
        }), 400

    user = create_user(
        full_name,
        company_name,
        email,
        password
    )

    if not user:
        return jsonify({
            "error": "Email already registered"
        }), 400

    return jsonify({
        "user_id": user["id"],
        "email": user["email"],
        "message": "Account created successfully"
    })


# ============================================
# LOGIN
# ============================================

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")


    if not email or not password:
        return jsonify({
            "error": "Email and password required"
        }),400


    user = verify_user(email, password)


    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }),401


    return jsonify({
        "user_id": user["id"],
        "email": user["email"],
        "message": "Login successful"
    })


# ============================================
# HISTORY (FIXED - NO CONFLICT)
# ============================================

# ALL USERS (ADMIN / DEBUG)
@app.route("/history", methods=["GET"])
def history_all():
    rows = get_history(limit=50)
    return jsonify(rows)


# SINGLE USER (MAIN DASHBOARD USE)
@app.route("/history/<int:user_id>", methods=["GET"])
def history_user(user_id):
    rows = get_history_by_user(user_id, limit=50)
    return jsonify(rows)


# ============================================
# DELETE (SINGLE + ALL)
# ============================================

@app.route("/delete/<int:row_id>", methods=["DELETE"])
def delete_row(row_id):
    delete_analysis(row_id)
    return jsonify({"status": "success"})


@app.route("/delete-all", methods=["DELETE"])
def delete_all():
    delete_all_history()
    return jsonify({"status": "success"})


# ============================================
# EXPORT CSV (ALL / USER)
# ============================================

@app.route("/export/csv", methods=["GET"])
def export_csv():
    user_id = request.args.get("user_id")

    if user_id:
        rows = get_history_by_user(int(user_id), limit=1000)
    else:
        rows = get_history(limit=1000)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["timestamp", "name", "score", "status", "ceo_summary"])

    for item in rows:
        timestamp = item.get("timestamp", "")
        data = item.get("data", {})
        campaigns = data.get("campaigns", [])
        ceo = data.get("ceo_summary", "")

        for c in campaigns:
            writer.writerow([
                timestamp,
                c.get("name", ""),
                c.get("score", 0),
                c.get("status", ""),
                ceo
            ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=campaign_iq.csv"
        }
    )


# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)