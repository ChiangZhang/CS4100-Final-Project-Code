// Claude AI disclosure:
// Prompts: For the frontend JavaScript, I want to be able to search for a song by name or paste a Spotify URL as the seed for the playlist. How can I implement these two modes of input and handle the form submission to generate the playlist based on the selected seed?

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

// ─── Seed-mode tab switching ────────────────────────────────────────────────
let seedMode = 'name';   // 'name' | 'url'

function switchTab(mode) {
    seedMode = mode;

    document.getElementById('tab-name').classList.toggle('active', mode === 'name');
    document.getElementById('tab-url').classList.toggle('active',  mode === 'url');

    document.getElementById('name-seed-panel').style.display = mode === 'name' ? 'block' : 'none';
    document.getElementById('url-seed-panel').style.display  = mode === 'url'  ? 'block' : 'none';

    // Reset state when switching
    setStatus('', '');
    if (mode === 'name') {
        clearUrlPreview();
    } else {
        selectedTrackName = '';
        document.getElementById('selected-song-info').style.display = 'none';
    }
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

// ─── Song search autocomplete (name mode) ───────────────────────────────────
let selectedTrackName = '';
let searchTimer = null;

const songInput    = document.getElementById('start-song');
const dropdown     = document.getElementById('song-dropdown');
const selectedInfo = document.getElementById('selected-song-info');

songInput.addEventListener('input', () => {
    selectedTrackName = '';
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
        item.addEventListener('mousedown', (e) => {
            e.preventDefault(); // stops input blur firing before selection commits
            selectedTrackName = item.dataset.name;
            songInput.value   = selectedTrackName;
            selectedInfo.textContent = `by ${item.dataset.artist}`;
            selectedInfo.style.display = 'block';
            dropdown.style.display = 'none';
        });
    });
}

document.addEventListener('click', e => {
    if (!e.target.closest('.song-search-wrap')) {
        dropdown.style.display = 'none';
    }
});

// ─── Spotify URL mode ───────────────────────────────────────────────────────
const spotifyInput = document.getElementById('spotify-url');

/** Show/hide the preview card under the URL input. */
function showUrlPreview(name, artist, topMoods) {
    document.getElementById('preview-name').textContent   = name;
    document.getElementById('preview-artist').textContent = artist;
    document.getElementById('preview-mood').textContent   =
        topMoods ? `Top moods: ${topMoods}` : '';
    document.getElementById('url-song-preview').style.display = 'block';
}

function clearUrlPreview() {
    document.getElementById('url-song-preview').style.display = 'none';
    document.getElementById('preview-name').textContent   = '';
    document.getElementById('preview-artist').textContent = '';
    document.getElementById('preview-mood').textContent   = '';
}

/** Basic client-side check: looks like a Spotify track URL? */
function isSpotifyTrackUrl(str) {
    return /open\.spotify\.com\/track\/[A-Za-z0-9]+/.test(str);
}

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

    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.font = '10px monospace';
    ctx.fillStyle = '#666';
    [0, 0.25, 0.5, 0.75, 1].forEach(v => {
        const y = PAD.top + cH * (1 - v);
        ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + cW, y); ctx.stroke();
        ctx.fillText(Math.round(v * 100) + '%', 2, y + 4);
    });

    ctx.fillStyle = '#666';
    ctx.textAlign = 'center';
    for (let i = 0; i < n; i++) {
        const x = PAD.left + (n === 1 ? cW / 2 : i / (n - 1) * cW);
        ctx.fillText(i + 1, x, H - PAD.bottom + 14);
    }
    ctx.textAlign = 'left';

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

        const last = playlist[n - 1];
        const v    = last.mood_values[mood] ?? 0;
        const x    = PAD.left + cW;
        const y    = PAD.top  + cH * (1 - v);
        ctx.fillStyle = color;
        ctx.font      = '9px monospace';
        ctx.fillText(mood, x + 3, y + 3);
    });

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
            const v   = track.mood_values[m] ?? 0;
            const pct = Math.round(v * 100);
            return `
            <div class="mini-bar-row">
                <span class="mini-bar-label" style="color:${moodColor(m)};font-weight:700">${m}</span>
                <div class="mini-bar-bg">
                    <div class="mini-bar-fill" style="width:${pct}%;background:${moodColor(m)}"></div>
                </div>
                <span class="mini-bar-pct" style="color:${moodColor(m)}">${pct}%</span>
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

    const endMood      = document.getElementById('end-mood').value.trim();
    const playlistSize = parseInt(document.getElementById('n-songs').value);
    const btn          = document.getElementById('generate-btn');

    // ── Validate seed depending on active tab ──────────────────────────────
    if (seedMode === 'name') {
        if (!selectedTrackName) {
            setStatus('Please search for and select a song from the dropdown.', 'error');
            return;
        }
    } else {
        const url = spotifyInput.value.trim();
        if (!url) {
            setStatus('Please paste a Spotify track URL.', 'error');
            return;
        }
        if (!isSpotifyTrackUrl(url)) {
            setStatus(
                'That doesn\'t look like a Spotify track URL. '
                + 'It should start with https://open.spotify.com/track/…',
                'error'
            );
            return;
        }
    }

    document.getElementById('playlist-container').style.display = 'none';
    btn.disabled    = true;
    btn.textContent = 'Generating…';

    // ── Branch: name search vs Spotify URL ─────────────────────────────────
    if (seedMode === 'name') {
        setStatus('Running mood-transition algorithm… this may take a few seconds.', 'loading');

        try {
            const genRes = await fetch(`${API_BASE}/api/generate-playlist`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    trackName: selectedTrackName,
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
            renderPlaylist(playlist, 'auto', endMood);

        } catch (err) {
            console.error(err);
            setStatus(`Error: ${err.message}`, 'error');
        }

    } else {
        // ── URL mode ──────────────────────────────────────────────────────
        const spotifyUrl = spotifyInput.value.trim();

        setStatus(
            'Fetching track features from Spotify… this may take a few seconds.',
            'loading'
        );

        try {
            const genRes = await fetch(`${API_BASE}/api/generate-from-url`, {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({
                    spotifyUrl,
                    endMood,
                    nSongs: playlistSize,
                }),
            });

            if (!genRes.ok) {
                const err = await genRes.json();
                throw new Error(err.error || 'Playlist generation failed.');
            }

            const { playlist } = await genRes.json();

            // Show a preview of the seed song (first track)
            if (playlist.length) {
                const seed = playlist[0];
                const topMoods = Object.entries(seed.mood_values)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 3)
                    .map(([m, v]) => `${m} ${Math.round(v * 100)}%`)
                    .join(', ');
                showUrlPreview(seed.track_name, seed.artists, topMoods);
            }

            setStatus('', '');
            renderPlaylist(playlist, 'auto', endMood);

        } catch (err) {
            console.error(err);
            setStatus(`Error: ${err.message}`, 'error');
        }
    }

    btn.disabled    = false;
    btn.textContent = 'Generate Playlist';
});