import re

# ============================================
# 1. SCORING ENGINE (guna kod anda)
# ============================================

def calculate_score(campaign_text):
    """
    Calculate campaign score based on metrics.
    Score starts at 50 and moves up/down.
    """

    score = 50

    text = campaign_text.upper()

    # ---------- ROAS ----------
    roas = re.search(r"ROAS[:\s]*([0-9.]+)", text)
    if roas:
        value = float(roas.group(1))

        if value >= 5:
            score += 40
        elif value >= 3:
            score += 20
        elif value >= 2:
            score += 10
        else:
            score -= 20

    # ---------- CPA ----------
    cpa = re.search(r"CPA[:\s]*([0-9.]+)", text)
    if cpa:
        value = float(cpa.group(1))

        if value <= 5:
            score += 20
        elif value <= 10:
            score += 10
        elif value <= 15:
            score += 0
        else:
            score -= 30

    # ---------- CTR ----------
    ctr = re.search(r"CTR[:\s]*([0-9.]+)", text)
    if ctr:
        value = float(ctr.group(1))

        if value >= 2:
            score += 20
        elif value >= 1:
            score += 10
        else:
            score -= 15

    score = max(0, min(score, 100))

    return score


# ============================================
# 2. STATUS DETECTION (guna kod anda)
# ============================================

def detect_status(score):
    if score >= 80:
        return "SCALE"
    elif score >= 50:
        return "WATCH"
    return "PAUSE"


# ============================================
# 3. INSIGHT GENERATOR (BARU)
# ============================================

def generate_insight(campaign_text, score, status):
    """
    Beri penjelasan kenapa status ini dipilih.
    """
    text = campaign_text.upper()
    reasons = []

    if status == "SCALE":
        roas = re.search(r"ROAS[:\s]*([0-9.]+)", text)
        if roas and float(roas.group(1)) >= 5:
            reasons.append("ROAS is excellent")
        else:
            reasons.append("Strong overall performance")

    elif status == "PAUSE":
        cpa = re.search(r"CPA[:\s]*([0-9.]+)", text)
        ctr = re.search(r"CTR[:\s]*([0-9.]+)", text)
        
        if cpa and float(cpa.group(1)) > 15:
            reasons.append("CPA is too high")
        if ctr and float(ctr.group(1)) < 1:
            reasons.append("CTR is weak")
        if not reasons:
            reasons.append("Multiple metrics underperforming")

    else:  # WATCH
        reasons.append("Performance is moderate — needs monitoring")

    return " + ".join(reasons) if reasons else "Performance within acceptable range"


# ============================================
# 4. IMPACT ESTIMATOR (BARU)
# ============================================

def estimate_impact(status, score):
    if status == "PAUSE":
        return "💰 Estimated loss: $30-50/day — Pause to stop burning budget"
    elif status == "SCALE":
        if score >= 80:
            return "📈 High potential: +30-40% ROAS — Scale aggressively"
        else:
            return "📈 Potential gain: +20-30% ROAS — Scale gradually"
    else:
        return "👀 Monitor performance — Keep watch on key metrics"


# ============================================
# 5. CEO SUMMARY (BARU)
# ============================================

def generate_summary(campaigns):
    if not campaigns:
        return "No campaigns to analyze."

    pause_count = sum(1 for c in campaigns if c.get("status") == "PAUSE")
    scale_count = sum(1 for c in campaigns if c.get("status") == "SCALE")

    if pause_count > 0 and scale_count > 0:
        return f"⚠️ {pause_count} campaign(s) draining budget, {scale_count} scalable — act now"
    elif pause_count > 0:
        return f"🔴 {pause_count} campaign(s) burning budget — pause immediately"
    elif scale_count > 0:
        return f"🟢 {scale_count} campaign(s) performing well — scale to maximize ROI"
    else:
        return "📊 All campaigns are stable — continue monitoring"


# ============================================
# 6. MAIN ENGINE (Panggil dari app.py)
# ============================================

def run_engine(raw_text):
    """
    Fungsi utama — panggil dari app.py.
    Input: raw text dari user
    Output: JSON structure
    """
    lines = raw_text.split("\n")
    campaigns = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Extract campaign name
        name_match = re.search(r"Campaign\s*([A-Za-z0-9 ]+)", line, re.IGNORECASE)
        if name_match:
            name = "Campaign " + name_match.group(1).strip().upper()
        else:
            name = "Unknown Campaign"

        # Calculate score
        score = calculate_score(line)

        # Detect status
        status = detect_status(score)

        # Generate insight
        insight = generate_insight(line, score, status)

        # Estimate impact
        impact_text = estimate_impact(status, score)

        # Reason & Impact (untuk UI consistency)
        if status == "SCALE":
            reason = f"Score {score}/100 — Strong performer"
            impact = "Increase budget by 20-30%"
        elif status == "WATCH":
            reason = f"Score {score}/100 — Needs monitoring"
            impact = "Review performance daily"
        else:
            reason = f"Score {score}/100 — Underperforming"
            impact = "Pause to stop burning budget"

        campaigns.append({
            "name": name,
            "score": score,
            "status": status,
            "reason": reason,
            "impact": impact,
            "insight": insight,
            "impact_text": impact_text
        })

    # Generate CEO summary
    ceo_summary = generate_summary(campaigns)

    # Calculate money at risk
    total_risk = 0
    for c in campaigns:
        if c.get("status") == "PAUSE":
            total_risk += 37  # estimate

    return {
        "greeting": "Good Morning 👋",
        "summary": {
            "money_at_risk": f"USD {total_risk}/day" if total_risk > 0 else "USD 0/day",
            "total_campaigns_checked": len(campaigns)
        },
        "ceo_summary": ceo_summary,
        "campaigns": campaigns
    }