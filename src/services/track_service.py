from urllib.parse import urlparse
import pandas as pd
import requests

from src.models.train_mood_model import FEATURE_COLS

class TrackService:
    
    @staticmethod
    def parse_spotify_track_id(spotify_url):
        path = urlparse(spotify_url).path
        return path.split('/')[-1]
    
    @staticmethod
    def get_reccobeats_id(spotify_id):
        try:
            url = "https://api.reccobeats.com/v1/track"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers, params={"ids": spotify_id})
            response_json = response.json()
            return response_json["content"][0]["id"]
        except:
            return None
        
    @staticmethod
    def get_audio_features(reccobeats_id):
        try:
            url = f"https://api.reccobeats.com/v1/track/{reccobeats_id}/audio-features"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            response_json = response.json()
            return pd.DataFrame([response_json])[FEATURE_COLS]
        except:
            return None
        
    def get_song_features(self, spotify_url):
        spotify_track_id = TrackService.parse_spotify_track_id(spotify_url)
        reccobeats_track_id = TrackService.get_reccobeats_id(spotify_track_id)
        if reccobeats_track_id is None:
            return None
        return TrackService.get_audio_features(reccobeats_track_id)