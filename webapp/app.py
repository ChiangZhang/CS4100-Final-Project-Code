import sys, os

# Add project root AND src/models to path so all imports resolve
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src', 'models'))

from flask import Flask, request, jsonify
from flask_cors import CORS
from src.services.track_service import TrackService
from src.services.mood_service import MoodService

app = Flask(__name__)
CORS(app)
track_service = TrackService()
mood_service = MoodService(input_dim=9)  # 9 audio features as input to the mood model)


@app.route('/api/track-features', methods=['POST'])
def get_track_features():
    data = request.get_json()
    spotify_url = data.get('spotifyUrl')
    if not spotify_url:
        return jsonify({'error': 'No URL provided'}), 400

    features = track_service.get_song_features(spotify_url)
    if features is None:
        return jsonify({'error': 'Could not fetch features for that track'}), 404

    return jsonify(features.to_dict(orient='records')[0])


@app.route('/api/generate-playlist', methods=['POST'])
def generate_playlist():
    data = request.get_json()

    spotify_url = data.get('spotifyUrl')
    start_mood  = data.get('startMood')
    end_mood    = data.get('endMood')
    n_songs     = int(data.get('nSongs', 10))

    if not spotify_url or not start_mood or not end_mood:
        return jsonify({'error': 'spotifyUrl, startMood, and endMood are required'}), 400

    # 1. Pull audio features for the seed track
    seed_features = track_service.get_song_features(spotify_url)
    if seed_features is None:
        return jsonify({'error': 'Could not fetch features for the seed track'}), 404

    # 2. Generate the mood-progressed playlist
    # MoodService.generate_playlist returns a list of dicts with at minimum:
    #   track_id, track_name, artists, spotify_url, predicted_mood
    try:
        playlist = mood_service.generate_playlist(
            seed_features=seed_features,
            start_mood=start_mood,
            end_mood=end_mood,
            n_songs=n_songs,
        )
    except Exception as e:
        return jsonify({'error': f'Playlist generation failed: {str(e)}'}), 500

    if not playlist:
        return jsonify({'error': 'No tracks found for the requested mood trajectory'}), 404

    return jsonify({'playlist': playlist})


if __name__ == '__main__':
    app.run(debug=True, port=5000)