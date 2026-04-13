# Ai disclosure: I use Claude to create and modify the code.
import sys, os

# Claude AI disclosure:
# Prompt: How to begin setting up a flask backend given the models that we have?
# Prompt: Which ports should we use for the backend and frontend during development?
# Prompt: When should I use GET or POST for my API endpoints?
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'models'))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'src', 'models'))  # so mood_model.py is importable

from flask import Flask, request, jsonify
from flask_cors import CORS
from hillClimbing import (
    load_dataset, find_song_by_name,
    generate_playlist as hc_generate_playlist, MOODS, Song
)
from services.track_service import TrackService, FEATURE_COLS
from services.mood_service import MoodService

app = Flask(__name__)
CORS(app)

# ── Load dataset once at startup ───────────────────────────────────────────────
_DATASET_PATH = os.path.join(project_root, 'models', 'final_mood_mapped_library.csv')
try:
    _ALL_SONGS = load_dataset(_DATASET_PATH)
    print(f"[startup] Loaded {len(_ALL_SONGS)} songs.")
except Exception as e:
    _ALL_SONGS = []
    print(f"[startup] WARNING: Could not load dataset: {e}")

_track_service = TrackService()
_mood_service  = MoodService(input_dim=len(FEATURE_COLS))


# ── Helpers ────────────────────────────────────────────────────────────────────
def _serialize_playlist(playlist_songs, end_mood):
    """Convert a list of Song objects into JSON-serialisable dicts."""
    n         = len(playlist_songs)
    start_val = playlist_songs[0].mood_values.get(end_mood, 0.0)
    result    = []
    for i, song in enumerate(playlist_songs):
        expected = start_val + (1.0 - start_val) * (i / (n - 1)) if n > 1 else start_val
        actual   = song.mood_values.get(end_mood, 0.0)
        result.append({
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
    return result


def _run_hill_climbing(songs, start_song, end_mood, n_songs):
    """Thin wrapper around hc_generate_playlist with shared defaults."""
    return hc_generate_playlist(
        songs            = songs,
        start_song       = start_song,
        target_mood      = end_mood,
        playlist_length  = n_songs,
        max_iterations   = 15000,
        initial_temp     = 1.0,
        cooling_rate     = 0.999,
        end_threshold    = 0.90,
        weight_expected  = 0.75,
        weight_smooth    = 0.25,
        stagnation_limit = 2000,
        seed             = 42,
        verbose          = False,
    )


# ── Search endpoint: live song name lookup ─────────────────────────────────────
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


# ── Generate playlist from dataset song name ───────────────────────────────────
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

    start_song = find_song_by_name(_ALL_SONGS, track_name)
    if start_song is None:
        return jsonify({'error': f"Song '{track_name}' not found in dataset."}), 404

    print(f"[seed/name] {start_song}")

    try:
        playlist_songs = _run_hill_climbing(_ALL_SONGS, start_song, end_mood, n_songs)
    except Exception as e:
        return jsonify({'error': f'Playlist generation failed: {str(e)}'}), 500

    if not playlist_songs:
        return jsonify({'error': 'No tracks found for the requested mood trajectory'}), 404

    return jsonify({'playlist': _serialize_playlist(playlist_songs, end_mood)})


# ── Generate playlist from a Spotify URL ──────────────────────────────────────
@app.route('/api/generate-from-url', methods=['POST'])
def generate_from_url():
    """
    Accepts a Spotify track URL, fetches its audio features via TrackService,
    predicts mood scores via MoodService, constructs a seed Song, then runs
    the same hill-climbing algorithm as the name-based endpoint.
    """
    data         = request.get_json()
    spotify_url  = data.get('spotifyUrl', '').strip()
    end_mood     = data.get('endMood', '').strip().lower()
    n_songs      = int(data.get('nSongs', 10))

    if not spotify_url or not end_mood:
        return jsonify({'error': 'spotifyUrl and endMood are required'}), 400
    if end_mood not in MOODS:
        return jsonify({'error': f"Unknown mood '{end_mood}'. Available: {MOODS}"}), 400
    if not _ALL_SONGS:
        return jsonify({'error': 'Dataset not loaded on server'}), 500

    # ── 1. Fetch audio features + metadata from ReccoBeats ────────────────────
    print(f"[seed/url] Fetching features for: {spotify_url}")
    song_df = _track_service.get_song_features(spotify_url)
    if song_df is None:
        return jsonify({
            'error': (
                'Could not fetch audio features for that Spotify URL. '
                'Make sure the URL is a valid track link '
                '(e.g. https://open.spotify.com/track/…).'
            )
        }), 422

    # ── 2. Predict mood scores ────────────────────────────────────────────────
    try:
        # MoodService.predict expects a DataFrame with FEATURE_COLS columns.
        # It returns a dict  {mood_name: score, …}  or similar — adapt if your
        # MoodService has a different interface.
        # predict_mood_vector expects a numpy array of shape (1, input_dim)
        import numpy as np
        from src.utils.mood_utils import MOODS as MOOD_LABELS
        feature_array = song_df[FEATURE_COLS].values.astype(np.float32)
        mood_vector = _mood_service.predict_mood_vector(feature_array)  # shape (n_moods,)
        mood_scores = {m: float(v) for m, v in zip(MOOD_LABELS, mood_vector[0])}
    except Exception as e:
        return jsonify({'error': f'Mood prediction failed: {str(e)}'}), 500

    # ── 3. Build a Song object compatible with hillClimbing ───────────────────
    spotify_id = TrackService.parse_spotify_track_id(spotify_url)
    track_name = song_df['track_name'].iloc[0] if 'track_name' in song_df.columns else 'Unknown Track'
    artists    = song_df['artists'].iloc[0]    if 'artists'    in song_df.columns else 'Unknown Artist'

    seed_song = Song(
        track_id    = spotify_id,
        track_name  = track_name,
        artists     = artists,
        mood_values = mood_scores,   # expects {mood: float} — same as dataset songs
    )

    print(f"[seed/url] Built seed: {seed_song}")

    # ── 4. Run hill climbing ──────────────────────────────────────────────────
    try:
        playlist_songs = _run_hill_climbing(_ALL_SONGS, seed_song, end_mood, n_songs)
    except Exception as e:
        return jsonify({'error': f'Playlist generation failed: {str(e)}'}), 500

    if not playlist_songs:
        return jsonify({'error': 'No tracks found for the requested mood trajectory'}), 404

    return jsonify({'playlist': _serialize_playlist(playlist_songs, end_mood)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
