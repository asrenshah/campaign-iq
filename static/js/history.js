// ================================
// LOAD HISTORY
// ================================
async function loadHistory() {
    if (!currentUser) {
        document.getElementById("historyPanel").innerHTML = `
            <div style="color:#6c7a92; text-align:center; padding:30px 0;">
                🔒 Please login to view history
            </div>
        `;
        return;
    }

    try {
        const res = await fetch(`/history/${currentUser}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        historyData = data || [];
        renderHistory();
    } catch (err) {
        console.error("History load error:", err);
        document.getElementById("historyPanel").innerHTML = `
            <div style="color:#ff5e6b; text-align:center; padding:30px 0;">
                ❌ Failed to load history
            </div>
        `;
    }
}

// ================================
// RENDER HISTORY (FIXED FILTER + SEARCH)
// ================================
function renderHistory() {
    const search = document.getElementById("historySearch")?.value?.toLowerCase() || "";

    let filtered = historyData;

    // FILTER + SEARCH LOGIC
    filtered = filtered.filter(item => {
        const matchFilter = item.data?.campaigns?.some(c => {
            if (currentFilter === "ALL") return true;
            return c?.status === currentFilter;
        });

        const matchSearch = item.data?.campaigns?.some(c => {
            return c?.name?.toLowerCase().includes(search);
        });

        return matchFilter && matchSearch;
    });

    // Update filter button active state
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active', 'active-all');
        if (btn.textContent.trim() === currentFilter) {
            btn.classList.add('active');
        } else if (currentFilter === "ALL" && btn.textContent.trim() === "ALL") {
            btn.classList.add('active-all');
        }
    });

    if (filtered.length === 0) {
        document.getElementById("historyPanel").innerHTML = `
            <div style="color:#6c7a92; text-align:center; padding:30px 0;">
                📭 No analyses match your search
            </div>
            <button class="clear-btn" onclick="clearAllHistory()">🗑 Clear All History</button>
        `;
        return;
    }

    let html = `<div style="margin-top:10px;">`;

    filtered.slice(0, 20).forEach(item => {
        const c = item.data?.campaigns?.[0];
        if (!c) return;

        let statusClass = "";
        if (c.status === "SCALE") statusClass = "scale";
        else if (c.status === "PAUSE") statusClass = "pause";
        else if (c.status === "WATCH") statusClass = "watch";

        const dataStr = JSON.stringify(item.data).replace(/'/g, "\\'");

        const displayName = (c.name && c.name.trim()) ? c.name : "Unnamed Campaign";

        html += `
            <div class="history-item" onclick='openHistory(${dataStr})'>
                <div class="row-flex">
                    <div>
                        <div class="name">${displayName} — ${c.score ?? 0}/100</div>
                        <div class="meta">
                            ${item.timestamp || 'Unknown'} • 
                            <span class="status-badge ${statusClass}">${c.status || 'UNKNOWN'}</span>
                        </div>
                    </div>
                    <button class="delete-btn" onclick="deleteHistory(event, ${item.id})">✕</button>
                </div>
            </div>
        `;
    });

    html += `<button class="clear-btn" onclick="clearAllHistory()">🗑 Clear All History</button>`;
    html += `</div>`;

    document.getElementById("historyPanel").innerHTML = html;
}

// ================================
// SET FILTER
// ================================
function setFilter(type) {
    currentFilter = type;
    renderHistory();
}

// ================================
// OPEN HISTORY DETAIL
// ================================
function openHistory(data) {
    let html = `
        <div style="margin-top:20px;">
            <h2 style="color:#e8edf2;">📊 Full Analysis</h2>
            <div style="color:#8b9bb5;font-size:12px;margin-bottom:10px;">
                ${new Date().toLocaleString()}
            </div>
            <div class="detail-box">
                <div style="margin-bottom:10px;color:#4f7aff;font-weight:600;">
                    🧠 CEO Summary
                </div>
                <div>${data.ceo_summary || 'No summary available'}</div>
            </div>
    `;

    html += `<hr style="margin:15px 0;border:1px solid #232b38;">`;

    if (data.campaigns && data.campaigns.length > 0) {
        data.campaigns.forEach(c => {
            const displayName = (c.name && c.name.trim()) ? c.name : "Unnamed Campaign";
            html += `
                <div class="campaign-card">
                    <div style="font-weight:600;">${displayName}</div>
                    <div style="color:#8b9bb5;font-size:13px;">
                        Score: ${c.score ?? 0}/100
                    </div>
                    <div style="color:#3dd68c;font-size:13px;margin-top:4px;">
                        Status: ${c.status || 'UNKNOWN'}
                    </div>
                    <div style="margin-top:6px;font-size:13px;">
                        ${c.reason || 'No reason provided'}
                    </div>
                    ${c.impact_text ? `<div style="margin-top:6px;font-size:12px;color:#f5a623;">${c.impact_text}</div>` : ''}
                    ${c.insight ? `<div style="margin-top:6px;font-size:12px;color:#8b9bb5;">${c.insight}</div>` : ''}
                </div>
            `;
        });
    } else {
        html += `<div style="color:#6c7a92;">No campaign data available</div>`;
    }

    html += `
            <button class="back-btn" onclick="loadHistory()">
                ← Back to History
            </button>
        </div>
    `;

    document.getElementById("historyPanel").innerHTML = html;
}

// ================================
// DELETE HISTORY
// ================================
async function deleteHistory(event, id) {
    event.stopPropagation();
    if (!confirm("Delete this analysis?")) return;

    try {
        await fetch(`/delete/${id}`, { method: "DELETE" });
        loadHistory();
    } catch (err) {
        alert("Failed to delete");
    }
}

async function clearAllHistory() {
    if (!confirm("Delete ALL history? This cannot be undone.")) return;

    try {
        await fetch("/delete-all", { method: "DELETE" });
        loadHistory();
    } catch (err) {
        alert("Failed to clear history");
    }
}

// ================================
// DOWNLOAD CSV
// ================================
function downloadCSV(status) {
    let url = `/export/csv/${status}`;
    if (currentUser) {
        url += `?user_id=${currentUser}`;
    }
    window.open(url, '_blank');
}