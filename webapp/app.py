import sys, os

project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'models'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from hillClimbing import (
    load_dataset, find_song_by_name,
    generate_playlist as hc_generate_playlist, MOODS
)

app = Flask(__name__)
CORS(app)

# ── Load dataset once at startup ──────────────────────────────────────────────
_DATASET_PATH = os.path.join(project_root, 'models', 'final_mood_mapped_library.csv')
try:
    _ALL_SONGS = load_dataset(_DATASET_PATH)
    print(f"[startup] Loaded {len(_ALL_SONGS)} songs.")
except Exception as e:
    _ALL_SONGS = []
    print(f"[startup] WARNING: Could not load dataset: {e}")


# ── Search endpoint: live song name lookup ────────────────────────────────────
@app.route('/api/search', methods=['GET'])
def search_songs():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])

    query_lower = query.lower()
    results = []
    for s in _ALL_SONGS:
        if query_lower in s.track_name.lower():
            results.append({
                'track_name': s.track_name,
                'artists':    s.artists,
                'track_id':   s.track_id,
            })
        if len(results) >= 8:
            break

    return jsonify(results)


# ── Generate playlist ─────────────────────────────────────────────────────────
@app.route('/api/generate-playlist', methods=['POST'])
def generate_playlist():
    data       = request.get_json()
    track_name = data.get('trackName', '').strip()
    end_mood   = data.get('endMood', '').strip().lower()
    n_songs    = int(data.get('nSongs', 10))

    if not track_name or not end_mood:
        return jsonify({'error': 'trackName and endMood are required'}), 400

    if end_mood not in MOODS:
        return jsonify({'error': f"Unknown mood '{end_mood}'. Available: {MOODS}"}), 400

    if not _ALL_SONGS:
        return jsonify({'error': 'Dataset not loaded on server'}), 500

    # Find seed song in dataset
    start_song = find_song_by_name(_ALL_SONGS, track_name)
    if start_song is None:
        return jsonify({'error': f"Song '{track_name}' not found in dataset. Try a different name."}), 404

    print(f"[seed] {start_song}")

    # Run hill climbing + SA + random restart
    try:
        playlist_songs = hc_generate_playlist(
            songs            = _ALL_SONGS,
            start_song       = start_song,
            target_mood      = end_mood,
            playlist_length  = n_songs,
            max_iterations   = 30000,
            initial_temp     = 1.0,
            cooling_rate     = 0.9999,
            end_threshold    = 0.90,
            weight_expected  = 0.75,
            weight_smooth    = 0.25,
            stagnation_limit = 3000,
            seed             = 42,
            verbose          = False,
        )
    except Exception as e:
        return jsonify({'error': f'Playlist generation failed: {str(e)}'}), 500

    if not playlist_songs:
        return jsonify({'error': 'No tracks found for the requested mood trajectory'}), 404

    # Serialise
    n         = len(playlist_songs)
    start_val = playlist_songs[0].mood_values.get(end_mood, 0.0)

    playlist = []
    for i, song in enumerate(playlist_songs):
        expected = start_val + (1.0 - start_val) * (i / (n - 1)) if n > 1 else start_val
        actual   = song.mood_values.get(end_mood, 0.0)
        playlist.append({
            'position':      i + 1,
            'track_id':      song.track_id,
            'track_name':    song.track_name,
            'artists':       song.artists,
            'target_mood':   end_mood,
            'mood_actual':   round(actual, 4),
            'mood_expected': round(expected, 4),
            'mood_values':   {m: round(v, 4) for m, v in song.mood_values.items()},
            'spotify_url':   f"https://open.spotify.com/track/{song.track_id}" if song.track_id else None,
            'is_seed':       i == 0,
        })

    return jsonify({'playlist': playlist})


if __name__ == '__main__':
    app.run(debug=True, port=5000)