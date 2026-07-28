import re

# ============================================
# 0. INPUT NORMALIZER (PINTU MASUK UTAMA)
# ============================================

def normalize_input(data):
    """
    Pintu masuk utama untuk semua jenis input.
    
    Input:
        - Text (string) - dari user paste
        - JSON (dict) - dari API / frontend
        - List - dari multiple sources
    
    Output:
        Normalized campaign objects
    """
    
    # ============================================
    # STEP 1 - Detect Input Type
    # ============================================
    
    # Jika string, raw_text
    if isinstance(data, str):
        return _parse_text(data)
    
    # Jika dict, mungkin JSON
    elif isinstance(data, dict):
        return _parse_json(data)
    
    # Jika list, multiple campaigns
    elif isinstance(data, list):
        return _parse_list(data)
    
    # Fallback
    else:
        return _parse_text(str(data))


# ============================================
# 0.1 - TEXT PARSER
# ============================================

def _parse_text(raw_text):
    """
    Parse text format (sedia ada dari run_engine)
    Return: List of campaign blocks
    """
    blocks = []
    current = []
    
    campaign_pattern = re.compile(
        r"^(Campaign|Campaign Name|Ad Set|Adset)\s*[:\-]",
        re.IGNORECASE
    )
    
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        if campaign_pattern.match(line) and current:
            blocks.append("\n".join(current))
            current = []
        
        current.append(line)
    
    if current:
        blocks.append("\n".join(current))
    
    if len(blocks) == 0:
        blocks = [raw_text.strip()]
    
    return blocks


# ============================================
# 0.2 - JSON PARSER
# ============================================

def _parse_json(json_data):
    """
    Parse JSON format
    Support:
        - {"campaigns": [...]}
        - {"campaign": {...}}
        - Single campaign object
    """
    blocks = []
    
    # Jika ada "campaigns" key
    if "campaigns" in json_data and isinstance(json_data["campaigns"], list):
        for campaign in json_data["campaigns"]:
            blocks.append(_campaign_to_block(campaign))
    
    # Jika ada "campaign" key (single)
    elif "campaign" in json_data:
        blocks.append(_campaign_to_block(json_data["campaign"]))
    
    # Jika direct single campaign object
    elif "name" in json_data or "spend" in json_data:
        blocks.append(_campaign_to_block(json_data))
    
    return blocks


# ============================================
# 0.3 - LIST PARSER
# ============================================

def _parse_list(data_list):
    """
    Parse list of campaigns
    """
    blocks = []
    for item in data_list:
        if isinstance(item, dict):
            blocks.append(_campaign_to_block(item))
        elif isinstance(item, str):
            blocks.append(item)
    return blocks


# ============================================
# 0.4 - CAMPAIGN TO BLOCK CONVERTER
# ============================================

def _campaign_to_block(campaign):
    """
    Convert campaign dict to text block
    Yang run_engine() faham
    """
    lines = []
    
    # Name
    if "name" in campaign:
        lines.append(f"Campaign: {campaign['name']}")
    
    # Metrics
    fields = [
        ("budget", "Budget"),
        ("spend", "Spend"),
        ("revenue", "Revenue"),
        ("roas", "ROAS"),
        ("ctr", "CTR"),
        ("cpc", "CPC"),
        ("cpa", "CPA"),
        ("conversions", "Conversions"),
        ("impressions", "Impressions"),
        ("clicks", "Clicks")
    ]
    
    for key, label in fields:
        if key in campaign and campaign[key] is not None:
            value = campaign[key]
            if isinstance(value, float):
                lines.append(f"{label}: {value:.2f}")
            else:
                lines.append(f"{label}: {value}")
    
    return "\n".join(lines)


# ============================================
# 1. SCORING ENGINE
# ============================================

def calculate_score(campaign_text):
    """
    Calculate campaign score based on metrics.
    Score starts at 50 and moves up/down.
    """

    score = 50

    text = campaign_text.upper()

    # ---------- ROAS ----------
    roas = re.search(r"ROAS[:\s]*([\d]+(?:\.[\d]+)?)", text)
    if roas:
        try:
            value = float(roas.group(1))
        except ValueError:
            value = 0

        if value >= 5:
            score += 40
        elif value >= 3:
            score += 20
        elif value >= 2:
            score += 10
        else:
            score -= 20

    # ---------- CPA ----------
    cpa = re.search(r"CPA[:\s]*([\d]+(?:\.[\d]+)?)", text)
    if cpa:
        try:
            value = float(cpa.group(1))
        except ValueError:
            value = 0

        if value <= 5:
            score += 20
        elif value <= 10:
            score += 10
        elif value <= 15:
            score += 0
        else:
            score -= 30

    # ---------- CTR ----------
    ctr = re.search(r"CTR[:\s]*([\d]+(?:\.[\d]+)?)", text)
    if ctr:
        try:
            value = float(ctr.group(1))
        except ValueError:
            value = 0

        if value >= 2:
            score += 20
        elif value >= 1:
            score += 10
        else:
            score -= 15

    score = max(0, min(score, 100))

    return score


# ============================================
# 1.5 EXTRACT METRICS
# ============================================

def extract_metrics(text):
    text = text.upper()

    patterns = {
        "budget": r"BUDGET[:\sRM$]*([\d]+(?:\.\d+)?)",
        "spend": r"SPEND[:\sRM$]*([\d]+(?:\.\d+)?)",
        "roas": r"ROAS[:\s]*([\d]+(?:\.\d+)?)",
        "ctr": r"CTR[:\s]*([\d]+(?:\.\d+)?)",
        "cpc": r"CPC[:\sRM$]*([\d]+(?:\.\d+)?)",
        "cpa": r"CPA[:\sRM$]*([\d]+(?:\.\d+)?)",
        "conversion": r"CONVERSIONS?[:\s]*([\d]+)",
    }

    metrics = {}

    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            try:
                metrics[key] = float(m.group(1))
            except:
                pass

    return metrics


# ============================================
# 2. STATUS DETECTION
# ============================================

def detect_status(score):
    if score >= 80:
        return "SCALE"
    elif score >= 50:
        return "WATCH"
    return "PAUSE"


# ============================================
# 3. INSIGHT GENERATOR
# ============================================

def generate_insight(metrics, score, status):

    insights = []

    # ---------- ROAS ----------
    roas = metrics.get("roas")
    if roas is not None:
        if roas >= 5:
            insights.append(f"✅ ROAS {roas} is excellent and highly profitable.")
        elif roas >= 3:
            insights.append(f"✅ ROAS {roas} is profitable.")
        else:
            insights.append(f"⚠️ ROAS {roas} is below the ideal target.")

    # ---------- CTR ----------
    ctr = metrics.get("ctr")
    if ctr is not None:
        if ctr >= 2:
            insights.append(f"✅ CTR {ctr}% indicates strong ad engagement.")
        elif ctr >= 1:
            insights.append(f"⚠️ CTR {ctr}% is average.")
        else:
            insights.append(f"❌ CTR {ctr}% is weak. Your creatives may need improvement.")

    # ---------- CPA ----------
    cpa = metrics.get("cpa")
    if cpa is not None:
        if cpa <= 5:
            insights.append(f"✅ CPA {cpa} is very efficient.")
        elif cpa <= 10:
            insights.append(f"✅ CPA {cpa} is within an acceptable range.")
        else:
            insights.append(f"❌ CPA {cpa} is too high.")

    # ---------- Recommendation ----------
    if status == "SCALE":
        insights.append("🚀 Recommendation: Increase budget by 20% while monitoring CPA.")
    elif status == "WATCH":
        insights.append("👀 Recommendation: Continue monitoring before making major changes.")
    else:
        insights.append("🛑 Recommendation: Pause the campaign and improve creatives or targeting.")

    return "\n".join(insights)


# ============================================
# 4. RECOMMENDATION ENGINE
# ============================================

def generate_recommendation(metrics, status):

    recommendation = []

    budget = metrics.get("budget")
    roas = metrics.get("roas")
    cpa = metrics.get("cpa")

    if status == "SCALE":
        if budget:
            new_budget = round(budget * 1.2, 2)
            recommendation.append(
                f"📈 Increase budget from ${budget:.0f} → ${new_budget:.0f}."
            )

        recommendation.append(
            "🎯 Review performance after additional spend."
        )

        if cpa is not None:
            recommendation.append(
                f"🛑 Stop scaling if CPA rises above {round(cpa * 1.2,2)}."
            )

        if roas is not None:
            recommendation.append(
                f"🛑 Stop scaling if ROAS falls below {max(2.5, round(roas-0.7,1))}."
            )

    elif status == "WATCH":

        recommendation.append(
            "👀 Keep monitoring for another 24 hours before making changes."
        )

    else:

        recommendation.append(
            "⛔ Pause this campaign and investigate the creatives, audience and landing page."
        )

    return "\n".join(recommendation)


# ============================================
# 5. HEALTH CALCULATOR
# ============================================

def calculate_health(score):
    if score >= 90:
        return "Excellent", "🟢"
    elif score >= 80:
        return "Very Good", "🟢"
    elif score >= 65:
        return "Good", "🟡"
    elif score >= 50:
        return "Average", "🟡"
    else:
        return "Poor", "🔴"


# ============================================
# 6. IMPACT ESTIMATOR
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
# 7. CEO SUMMARY
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
# 8. MAIN ENGINE (VERSION 3 - NORMALIZED INPUT)
# ============================================

def run_engine(raw_text):
    """
    Main Decision Engine
    Input:
        Raw text (single atau multiple campaigns)
    Output:
        JSON untuk frontend
    """

    # ============================================
    # STEP 1 - Normalize input
    # ============================================

    blocks = normalize_input(raw_text)

    # ============================================
    # STEP 2 - Analyze setiap campaign
    # ============================================

    campaigns = []

    for block in blocks:

        if not block.strip():
            continue

        # Cari nama campaign
        name = "Unknown Campaign"

        m = re.search(
            r"(?:Campaign|Campaign Name|Ad Set|Adset)\s*[:\-]\s*(.+)",
            block,
            re.IGNORECASE
        )

        if m:
            name = m.group(1).strip()

        # Calculate score
        score = calculate_score(block)

        # Calculate health
        health, health_icon = calculate_health(score)

        # Extract metrics
        metrics = extract_metrics(block)

        # Detect status
        status = detect_status(score)

        # Generate insight
        insight = generate_insight(metrics, score, status)

        # Generate recommendation
        recommendation = generate_recommendation(metrics, status)

        # Estimate impact
        impact_text = estimate_impact(status, score)

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

            "health": health,

            "health_icon": health_icon,

            "metrics": metrics,

            "reason": reason,

            "impact": impact,

            "insight": insight,

            "impact_text": impact_text,

            "recommendation": recommendation

        })

    # ============================================
    # STEP 3 - CEO Summary
    # ============================================

    ceo_summary = generate_summary(campaigns)

    total_risk = sum(
        37 for c in campaigns
        if c["status"] == "PAUSE"
    )

    return {

        "greeting": "Good Morning 👋",

        "summary": {

            "money_at_risk":
                f"USD {total_risk}/day" if total_risk else "USD 0/day",

            "total_campaigns_checked":
                len(campaigns)

        },

        "ceo_summary": ceo_summary,

        "campaigns": campaigns

    }