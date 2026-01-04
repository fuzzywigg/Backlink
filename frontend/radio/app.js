document.addEventListener('DOMContentLoaded', () => {
    // Basic status simulator for now
    const statusIndicator = document.getElementById('connection-status');
    const artistEl = document.getElementById('current-artist');
    const trackEl = document.getElementById('current-track');
    const logEl = document.getElementById('intention-log');

    // Simulate connecting
    setTimeout(() => {
        statusIndicator.innerText = 'ONLINE';
        statusIndicator.classList.remove('offline');
        statusIndicator.classList.add('online');

        artistEl.innerText = "The Hive Mind";
        trackEl.innerText = "Neural Handshake [Systems Online]";

        addLog("RADIO_BEE", "Connection established. Frequencies open.");
    }, 1500);

    // Function to add intention logs
    function addLog(bee, message, status = "BROADCAST") {
        const li = document.createElement('li');
        const now = new Date().toLocaleTimeString();
        let statusHtml = "";
        if (status !== "BROADCAST") {
            statusHtml = `<span class="status-tag status-${status.toLowerCase()}">[${status}]</span> `;
        }

        li.innerHTML = `<span class="timestamp">[${now}]</span> ${statusHtml}<span class="bee-id">${bee}</span>: ${message}`;
        li.className = `log-item type-${status.toLowerCase()}`;
        logEl.prepend(li); // Newest top
    }

    const needsEl = document.getElementById('needs-list');

    // Function to render a need
    function addNeed(need) {
        // Remove empty state if present
        const empty = needsEl.querySelector('.empty-state');
        if (empty) empty.remove();

        const item = document.createElement('div');
        item.className = 'need-item';
        item.id = need.id;

        item.innerHTML = `
            <span class="urgency">[OPEN]</span>
            <span class="need-type">${need.type}</span>: ${need.description} ($${need.amount})
            <button class="donate-btn" onclick="fundNeed('${need.id}')">FUND</button>
        `;
        needsEl.appendChild(item);
    }

    // Simulate incoming need after a few seconds
    setTimeout(() => {
        addNeed({
            id: 'need-123',
            type: 'COMPUTE',
            description: 'Background indexing paused. Need GPU time.',
            amount: 5.00
        });
        addLog("SYSTEM", "New resource request logged.", "ALERT");
    }, 4000);

    // Global handler for funding (since we inject HTML string)
    window.fundNeed = (id) => {
        const btn = document.querySelector(`#${id} .donate-btn`);
        if (btn) {
            btn.innerText = "PROCESSING...";
            setTimeout(() => {
                btn.innerText = "FUNDED";
                btn.disabled = true;
                addLog("TREASURY_BEE", `Need ${id} funded. Resources allocated.`);
            }, 1000);
        }
    };

    // TODO: In the future, this will poll an endpoint (e.g., /api/radio/status) 
    // to get real-time info from the Python backend or Goose FM MCP.
});
