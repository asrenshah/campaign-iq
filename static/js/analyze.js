// ================================
// ANALYZE ENGINE
// ================================

async function analyze() {
    const btn = document.getElementById('analyzeBtn');
    const outputDiv = document.getElementById('output');

    const rawInput = document.getElementById('inputData').value.trim();

    if (!rawInput) {
        alert('Please paste campaign data first');
        return;
    }

    if (!currentUser) {
        alert('Please login first');
        return;
    }

    let payload;
    try {
        payload = JSON.parse(rawInput);
    } catch {
        payload = { ads: rawInput };
    }

    payload.user_id = currentUser;

    btn.disabled = true;
    btn.innerHTML = "Analyzing...";

    outputDiv.classList.add('visible');
    outputDiv.innerHTML = `
        <div style="text-align:center;padding:30px;">
            <div style="font-size:18px;">🧠 AI Engine Processing</div>
            <div style="color:#6c7a92;margin-top:10px;">
                Analyzing ROAS, CPA, CTR signals...
            </div>
            <div style="margin-top:10px;color:#4f7aff;">
                Generating insights...
            </div>
        </div>
    `;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        
        console.log("AI RESPONSE:", result);

        // ================================
        // FIX: SANITIZE DATA — NO "Unknown Campaign"
        // ================================
        const campaigns = (result.campaigns || []).map(c => ({
            name: (c.name && c.name.trim()) ? c.name : "Unnamed Campaign",
            score: c.score ?? 0,
            status: c.status || "WATCH",
            health: c.health || "Unknown",
            health_icon: c.health_icon || "⚪",
            reason: c.reason || "",
            impact: c.impact || "",
            insight: c.insight || "",
            impact_text: c.impact_text || "",
            recommendation: c.recommendation || ""
        }));

        // Sort by score descending
        campaigns.sort((a, b) => (b.score || 0) - (a.score || 0));

        const firstCampaign = campaigns.length > 0 ? campaigns[0] : null;

        let html = "";

        html += `
        <div class="hero-dashboard">

            <div class="greeting">
                ${result.greeting ?? "Good Morning 👋"}
            </div>

            <div class="hero-health">
                <div class="hero-title">
                    ${firstCampaign ? firstCampaign.health_icon : "⚪"}
                    Campaign Health
                </div>

                <div class="hero-score">
                    ${firstCampaign ? firstCampaign.health : "No Data"}
                </div>

                <div class="hero-subtitle">
                    AI Decision Engine is monitoring
                    ${result.summary?.total_campaigns_checked ?? 0}
                    campaign(s)
                </div>
            </div>

            <div class="kpi-grid">

                <div class="kpi-item">
                    <div class="kpi-label">💰 Money at Risk</div>
                    <div class="kpi-value orange">
                        ${result.summary?.money_at_risk ?? "USD 0/day"}
                    </div>
                </div>

                <div class="kpi-item">
                    <div class="kpi-label">📊 Campaigns</div>
                    <div class="kpi-value">
                        ${result.summary?.total_campaigns_checked ?? 0}
                    </div>
                </div>

                <div class="kpi-item">
                    <div class="kpi-label">⭐ Portfolio Score</div>
                    <div class="kpi-value blue">
                        ${firstCampaign ? firstCampaign.score : "--"}
                    </div>
                </div>

            </div>

        </div>
        `;

        if (result.ceo_summary) {
            html += `<div class="ceo-summary">🧠 ${result.ceo_summary}</div>`;
        }

        html += `<hr><div style="font-size:14px;color:#8b9bb5;margin-bottom:10px;">🎯 Ranked Campaign Intelligence</div>`;

        if (campaigns.length === 0) {
            html += `<div class="empty-state"><div class="icon">📭</div><div class="title">No campaigns found</div><div class="sub">Paste campaign data to generate AI insights</div></div>`;
        } else {
            campaigns.forEach(c => {
                let color = "";
                let badge = "";

                if (c.status === "PAUSE") {
                    color = "urgent";
                    badge = `<span style="color:#ff5e6b;font-weight:700;">● PAUSE</span>`;
                } else if (c.status === "SCALE") {
                    color = "growth";
                    badge = `<span style="color:#3dd68c;font-weight:700;">● SCALE</span>`;
                } else if (c.status === "WATCH") {
                    color = "watch";
                    badge = `<span style="color:#f5a623;font-weight:700;">● WATCH</span>`;
                } else {
                    color = "watch";
                    badge = `<span style="color:#6c7a92;font-weight:700;">● ${c.status || 'REVIEW'}</span>`;
                }

                const insightHtml = c.insight ? c.insight.replace(/\n/g, "<br>") : "";

                html += `
                    <div class="action-card ${color}">
                        <div class="campaign">${badge} <span>${c.name}</span></div>
                        <div class="detail">${c.reason || 'No reason provided'}</div>
                        <div class="impact">${c.impact || 'No impact specified'}</div>
                        ${insightHtml ? `<div class="ai-highlight">🧠 ${insightHtml}</div>` : ''}
                        ${c.recommendation ? `<div class="recommendation">🎯 ${c.recommendation.replace(/\n/g, "<br>")}</div>` : ''}
                        ${c.impact_text ? `<div class="impact-text">${c.impact_text}</div>` : ''}
                        <div class="detail" style="margin-top:6px;opacity:0.6;">Score: ${c.score}/100</div>
                    </div>
                `;
            });
        }

        html += `
            <hr>
            <div style="text-align:center;color:#4f5a6e;font-size:12px;">
                Campaign IQ — AI Decision Engine • ${new Date().toLocaleDateString('en-US', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })}
            </div>
        `;

        outputDiv.innerHTML = html;

        // ================================
        // RESET SEARCH + FILTER SELEPAS ANALYZE
        // ================================
        await loadHistory();

        // Reset search box
        document.getElementById("historySearch").value = "";

        // Reset filter to ALL
        currentFilter = "ALL";

        // Render semula dengan clean state
        renderHistory();

    } catch (error) {
        outputDiv.innerHTML = `
            <div style="color:#ff5e6b;text-align:center;padding:20px;">
                ❌ Error: ${error.message || 'Something went wrong.'}
            </div>
        `;
    }

    btn.disabled = false;
    btn.innerHTML = "☀️ Generate Briefing";
}