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
    function addLog(bee, message) {
        const li = document.createElement('li');
        const now = new Date().toLocaleTimeString();
        li.innerHTML = `<span class="timestamp">[${now}]</span> <span class="bee-id">${bee}</span>: ${message}`;
        logEl.prepend(li); // Newest top
    }

    // Example interaction
    document.querySelector('.donate-btn').addEventListener('click', (e) => {
        e.target.innerText = "PROCESSING...";
        setTimeout(() => {
            e.target.innerText = "FUNDED";
            e.target.disabled = true;
            addLog("TREASURY_BEE", "Received funds. Resuming background indexing.");
        }, 1000);
    });

    // TODO: In the future, this will poll an endpoint (e.g., /api/radio/status) 
    // to get real-time info from the Python backend or Goose FM MCP.
});
