from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# ============================================
# PHASE 3A: BRAIN SCORE SYSTEM
# ============================================

def calculate_score(campaign):
    score = 50  # base score

    # ROAS logic
    if "roas" in campaign:
        if campaign["roas"] >= 4:
            score += 40
        elif campaign["roas"] >= 2:
            score += 20
        else:
            score -= 20

    # CPA logic
    if "cpa" in campaign:
        if campaign["cpa"] > 10:
            score -= 30
        elif campaign["cpa"] < 5:
            score += 10

    # CTR logic
    if "ctr" in campaign:
        if campaign["ctr"] < 1:
            score -= 25
        elif campaign["ctr"] > 3:
            score += 15

    # clamp score
    return max(0, min(100, score))


# ============================================
# PHASE 3B: INSIGHT ENGINE
# ============================================

def generate_insight(campaign):
    reasons = []

    if "cpa" in campaign and campaign["cpa"] > 10:
        reasons.append(f"CPA ${campaign['cpa']} is above safe threshold (42% higher)")

    if "roas" in campaign and campaign["roas"] < 2:
        reasons.append(f"ROAS {campaign['roas']}x is too low")

    if "ctr" in campaign and campaign["ctr"] < 1:
        reasons.append(f"CTR {campaign['ctr']}% indicates weak engagement")

    if "roas" in campaign and campaign["roas"] >= 4:
        reasons.append(f"ROAS {campaign['roas']}x shows strong performance")

    if "ctr" in campaign and campaign["ctr"] > 3:
        reasons.append(f"CTR {campaign['ctr']}% indicates strong engagement")

    return " + ".join(reasons) if reasons else "Performance within acceptable range"


def estimate_impact(campaign):
    if campaign.get("status") == "PAUSE":
        return "💰 Estimated loss: $37/day — Pause to stop burning budget"
    elif campaign.get("status") == "SCALE":
        return "📈 Potential gain: +20–30% ROAS — Scale to maximize returns"
    else:
        return "👀 Monitor performance — Keep watch on key metrics"


def generate_ceo_summary(campaigns):
    if not campaigns:
        return "No campaigns to analyze."

    pause_count = sum(1 for c in campaigns if c.get("status") == "PAUSE")
    scale_count = sum(1 for c in campaigns if c.get("status") == "SCALE")
    watch_count = sum(1 for c in campaigns if c.get("status") == "WATCH")

    if pause_count > 0 and scale_count > 0:
        return f"⚠️ {pause_count} campaign{'s' if pause_count > 1 else ''} {'is' if pause_count == 1 else 'are'} draining budget, while {scale_count} {'is' if scale_count == 1 else 'are'} scalable — act now to save ${pause_count * 37}/day"
    elif pause_count > 0:
        return f"🔴 {pause_count} campaign{'s' if pause_count > 1 else ''} {'is' if pause_count == 1 else 'are'} burning budget — pause immediately to save ${pause_count * 37}/day"
    elif scale_count > 0:
        return f"🟢 {scale_count} campaign{'s' if scale_count > 1 else ''} {'is' if scale_count == 1 else 'are'} performing well — scale to maximize ROI"
    else:
        return "📊 All campaigns are stable — continue monitoring"


# ============================================
# PARSER ENGINE
# ============================================

def parse_campaigns(raw_text):
    campaigns = []

    lines = raw_text.split("\n")

    for line in lines:
        line = line.lower().strip()
        
        # Skip empty lines
        if not line:
            continue

        # Extract metrics using regex
        name_match = re.search(r"campaign\s*([a-z0-9 ]+)", line)
        roas_match = re.search(r"roas\s*([\d.]+)", line)
        cpa_match = re.search(r"cpa\s*([\d.]+)", line)
        ctr_match = re.search(r"ctr\s*([\d.]+)", line)

        campaign = {}

        # Extract campaign name
        if name_match:
            campaign["name"] = "Campaign " + name_match.group(1).strip().upper()
        else:
            campaign["name"] = "Unknown Campaign"

        # Extract metrics
        if roas_match:
            campaign["roas"] = float(roas_match.group(1))

        if cpa_match:
            campaign["cpa"] = float(cpa_match.group(1))

        if ctr_match:
            campaign["ctr"] = float(ctr_match.group(1))

        # ============================================
        # Calculate score
        # ============================================
        campaign["score"] = calculate_score(campaign)

        # ============================================
        # Status logic based on SCORE
        # ============================================
        if campaign["score"] >= 75:
            campaign["status"] = "SCALE"
            campaign["reason"] = f"Score {campaign['score']}/100 — Strong performer"
            campaign["impact"] = "Increase budget by 20-30%"
            
        elif campaign["score"] >= 40:
            campaign["status"] = "WATCH"
            campaign["reason"] = f"Score {campaign['score']}/100 — Needs monitoring"
            campaign["impact"] = "Review performance daily"
            
        else:
            campaign["status"] = "PAUSE"
            campaign["reason"] = f"Score {campaign['score']}/100 — Underperforming"
            campaign["impact"] = "Pause to stop burning budget"

        # ============================================
        # PHASE 3B: INSIGHT ENGINE
        # ============================================
        campaign["insight"] = generate_insight(campaign)
        campaign["impact_text"] = estimate_impact(campaign)

        campaigns.append(campaign)

    return campaigns


# ============================================
# API ROUTES
# ============================================
@app.route("/")
def home():
    return "Campaign IQ API is running — Insight Engine Active"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    raw_text = data.get("ads", "")
    
    # Parse campaigns from raw text
    campaigns = parse_campaigns(raw_text)
    
    # Calculate money at risk (estimate)
    total_risk = sum([
        int(c.get("cpa", 0) * 3) if c.get("status") == "PAUSE" else 0 
        for c in campaigns
    ])
    
    # Generate CEO Summary
    ceo_summary = generate_ceo_summary(campaigns)
    
    return {
        "greeting": "Good Morning 👋",
        "summary": {
            "money_at_risk": f"USD {total_risk}/day" if total_risk > 0 else "USD 0/day",
            "total_campaigns_checked": len(campaigns)
        },
        "ceo_summary": ceo_summary,
        "campaigns": campaigns
    }

@app.route("/join", methods=["POST"])
def join():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Email required"}), 400

    # Simple email validation
    if "@" not in email or "." not in email:
        return jsonify({"status": "error", "message": "Invalid email"}), 400

    # Save to waitlist.txt
    with open("waitlist.txt", "a") as f:
        f.write(email + "\n")

    print(f"📧 New waitlist signup: {email}")

    return jsonify({"status": "success", "message": "Added to waitlist"})

if __name__ == "__main__":
    app.run(debug=True)