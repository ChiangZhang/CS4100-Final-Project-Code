// ─── Config ────────────────────────────────────────────────────────────────
const API_BASE = 'http://localhost:5000';

// ─── Helpers ───────────────────────────────────────────────────────────────


function setStatus(msg, type = '') {
    const el = document.getElementById('status-msg');
    el.textContent = msg;
    el.className = type ? `status-${type}` : '';
    el.style.display = msg ? 'block' : 'none';
}

function toggleForm() {
    const el = document.getElementById('mood-selection');
    el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


// ─── Form submission ───────────────────────────────────────────────────────

document.getElementById('mood-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const startMood = document.getElementById('start-mood').value.trim();
    const endMood = document.getElementById('end-mood').value.trim();
    const playlistSize = parseInt(document.getElementById('n-songs').value);
    const spotifyUrl = document.getElementById('start-song').value.trim();
    const btn = document.getElementById('generate-btn');

    // Validation
    if (!spotifyUrl) {
        setStatus('Please enter a Spotify track link.', 'error');
        return;
    }

    console.log('Form submitted with:', { startMood, endMood, playlistSize, spotifyUrl });

    btn.disabled = true;
    btn.textContent = 'Fetching features…';
    setStatus('Fetching track features from Spotify…', 'loading');

    try {
        // Step 1 — fetch seed track features only
        const featRes = await fetch(`http://localhost:5000/api/track-features`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ spotifyUrl }),
        });

        if (!featRes.ok) {
            const err = await featRes.json();
            throw new Error(err.error || 'Could not fetch track features.');
        }

        const features = await featRes.json();
        console.log('Seed track features:', features);

        // Stop here — do NOT call generate-playlist yet
        setStatus('Seed track features fetched. Check console for output.', 'success');

    } catch (err) {
        console.error(err);
        setStatus(`Error: ${err.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Generate Playlist';
    }
});