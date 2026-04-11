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

// ─── Mood colours ───────────────────────────────────────────────────────────
const MOOD_COLORS = {
    calm:      '#7ec8e3',
    energetic: '#ff6b35',
    happy:     '#ffd166',
    sad:       '#6c91c2',
    dark:      '#7b2d8b',
    romantic:  '#e84393',
    focus:     '#06d6a0',
    hype:      '#ef233c',
};
function moodColor(mood) { return MOOD_COLORS[mood] || '#888'; }

// ─── Song search autocomplete ───────────────────────────────────────────────
let selectedTrackName = '';   // the exact name confirmed by the user
let searchTimer = null;

const songInput    = document.getElementById('start-song');
const dropdown     = document.getElementById('song-dropdown');
const selectedInfo = document.getElementById('selected-song-info');

songInput.addEventListener('input', () => {
    selectedTrackName = '';           // clear confirmed selection on new typing
    selectedInfo.style.display = 'none';
    clearTimeout(searchTimer);
    const q = songInput.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }

    searchTimer = setTimeout(async () => {
        try {
            const res  = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(q)}`);
            const hits = await res.json();
            renderDropdown(hits);
        } catch { dropdown.style.display = 'none'; }
    }, 250);
});

function renderDropdown(hits) {
    if (!hits.length) { dropdown.style.display = 'none'; return; }
    dropdown.innerHTML = hits.map(h => `
        <div class="dropdown-item"
             data-name="${escapeHtml(h.track_name)}"
             data-artist="${escapeHtml(h.artists)}">
            <span class="di-name">${escapeHtml(h.track_name)}</span>
            <span class="di-artist">${escapeHtml(h.artists)}</span>
        </div>`).join('');
    dropdown.style.display = 'block';

    dropdown.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('mousedown', () => {   // mousedown fires before blur
            selectedTrackName = item.dataset.name;
            songInput.value   = selectedTrackName;
            selectedInfo.textContent = `by ${item.dataset.artist}`;
            selectedInfo.style.display = 'block';
            dropdown.style.display = 'none';
        });
    });
}

// Close dropdown when clicking elsewhere
document.addEventListener('click', e => {
    if (!e.target.closest('.song-search-wrap')) dropdown.style.display = 'none';
});

// ─── Mood progression chart ─────────────────────────────────────────────────
function drawMoodChart(playlist) {
    const canvas = document.getElementById('mood-chart');
    const MOODS  = ['calm','energetic','happy','sad','dark','romantic','focus','hype'];
    const n      = playlist.length;

    const W = canvas.clientWidth || 600;
    const H = 240;
    const PAD = { top: 16, right: 16, bottom: 36, left: 36 };
    const cW  = W - PAD.left - PAD.right;
    const cH  = H - PAD.top  - PAD.bottom;

    canvas.width  = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    // Background
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, W, H);

    // Grid
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#666';
    [0, 0.25, 0.5, 0.75, 1].forEach(v => {
        const y = PAD.top + cH * (1 - v);
        ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + cW, y); ctx.stroke();
        ctx.fillText(Math.round(v * 100) + '%', 2, y + 4);
    });

    // X labels
    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    for (let i = 0; i < n; i++) {
        const x = PAD.left + (n === 1 ? cW / 2 : i / (n - 1) * cW);
        ctx.fillText(i + 1, x, H - PAD.bottom + 14);
    }
    ctx.textAlign = 'left';

    // One line per mood
    MOODS.forEach(mood => {
        const color = moodColor(mood);
        ctx.strokeStyle = color;
        ctx.lineWidth   = 1.5;
        ctx.beginPath();
        playlist.forEach((track, i) => {
            const v = track.mood_values[mood] ?? 0;
            const x = PAD.left + (n === 1 ? cW / 2 : i / (n - 1) * cW);
            const y = PAD.top  + cH * (1 - v);
            i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        });
        ctx.stroke();

        // End-point label
        const last  = playlist[n - 1];
        const v     = last.mood_values[mood] ?? 0;
        const x     = PAD.left + cW;
        const y     = PAD.top  + cH * (1 - v);
        ctx.fillStyle = color;
        ctx.font      = '9px monospace';
        ctx.fillText(mood, x + 3, y + 3);
    });

    // Legend
    const legend = document.getElementById('mood-legend');
    legend.innerHTML = MOODS.map(m =>
        `<span style="font-size:0.72rem;color:${moodColor(m)};display:flex;align-items:center;gap:4px;">
            <span style="display:inline-block;width:20px;height:2px;background:${moodColor(m)};vertical-align:middle;"></span>${m}
         </span>`
    ).join('');
}

// ─── Render playlist ────────────────────────────────────────────────────────
function renderPlaylist(playlist, startMood, endMood) {
    const container = document.getElementById('playlist-tracks');
    const meta      = document.getElementById('playlist-meta');

    meta.textContent = `${playlist.length} songs · ${startMood} → ${endMood}`;

    // Draw mood chart
    drawMoodChart(playlist);
    document.getElementById('mood-chart-wrap').style.display = 'block';

    container.innerHTML = '';

    const MOODS_ORDER = ['calm','energetic','happy','sad','dark','romantic','focus','hype'];

    playlist.forEach((track) => {
        const spotifyBtn = track.spotify_url
            ? `<a class="spotify-btn" href="${escapeHtml(track.spotify_url)}"
                  target="_blank" rel="noopener">▶ Open</a>`
            : '';

        const seedBadge = track.is_seed
            ? `<span class="seed-badge">🎵 Your Song</span>`
            : '';

        const allMoodBars = MOODS_ORDER.map(m => {
            const v      = track.mood_values[m] ?? 0;
            const pct    = Math.round(v * 100);
            const isKey  = true;
            return `
            <div class="mini-bar-row">
                <span class="mini-bar-label" style="color:${isKey ? moodColor(m) : '#555'};font-weight:${isKey ? 700 : 400}">${m}</span>
                <div class="mini-bar-bg">
                    <div class="mini-bar-fill"
                         style="width:${pct}%;background:${moodColor(m)};opacity:${isKey ? 1 : 0.35}">
                    </div>
                </div>
                <span class="mini-bar-pct" style="color:${isKey ? moodColor(m) : '#555'}">${pct}%</span>
            </div>`;
        }).join('');

        const card = document.createElement('div');
        card.className = `track-card${track.is_seed ? ' seed-card' : ''}`;
        card.innerHTML = `
            <div class="track-number">${escapeHtml(String(track.position))}</div>
            <div class="track-info">
                <div class="track-name">${escapeHtml(track.track_name || '—')} ${seedBadge}</div>
                <div class="track-artist">${escapeHtml(track.artists || '')}</div>
                <div class="all-mood-bars">${allMoodBars}</div>
            </div>
            <div class="track-actions">${spotifyBtn}</div>`;

        container.appendChild(card);
    });

    const playlistSection = document.getElementById('playlist-container');
    playlistSection.style.display = 'block';
    playlistSection.scrollIntoView({ behavior: 'smooth' });
}

// ─── Form submission ────────────────────────────────────────────────────────
document.getElementById('mood-form').addEventListener('submit', async function (e) {
    e.preventDefault();

    const startMood    = "calm"; //placeholder since start mood is determined by the seed song
    const endMood      = document.getElementById('end-mood').value.trim();
    const playlistSize = parseInt(document.getElementById('n-songs').value);
    const btn          = document.getElementById('generate-btn');

    // Must have a confirmed selection from the dropdown
    if (!selectedTrackName) {
        setStatus('Please search for and select a song from the dropdown.', 'error');
        return;
    }

    document.getElementById('playlist-container').style.display = 'none';
    btn.disabled    = true;
    btn.textContent = 'Generating…';
    setStatus('Running mood-transition algorithm… this may take a few seconds.', 'loading');

    try {
        const genRes = await fetch(`${API_BASE}/api/generate-playlist`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                trackName: selectedTrackName,
                startMood,
                endMood,
                nSongs: playlistSize,
            }),
        });

        if (!genRes.ok) {
            const err = await genRes.json();
            throw new Error(err.error || 'Playlist generation failed.');
        }

        const { playlist } = await genRes.json();
        setStatus('', '');
        renderPlaylist(playlist, startMood, endMood);

    } catch (err) {
        console.error(err);
        setStatus(`Error: ${err.message}`, 'error');
    } finally {
        btn.disabled    = false;
        btn.textContent = 'Generate Playlist';
    }
});