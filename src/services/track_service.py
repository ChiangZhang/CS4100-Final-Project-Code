from urllib.parse import urlparse
import pandas as pd
import requests

# Defined here directly to avoid circular/missing import from train_mood_model
FEATURE_COLS = [
    'danceability', 'energy', 'loudness', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
]

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
        
    @staticmethod
    def get_track_details(reccobeats_id):
        try:
            url = f"https://api.reccobeats.com/v1/track/{reccobeats_id}"
            headers = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers)
            response_json = response.json()
            
            artists_list = response_json.get("artists", [])
            if artists_list:
                artists_str = ";".join([artist.get("name", "Unknown Artist") for artist in artists_list])
            else:
                artists_str = "Unknown Artist"
            
            track_info = {
                "track_name": response_json.get("name", "Unknown Track"),
                "artists": artists_str
            }

            return pd.DataFrame([track_info])

        except:
            return None
        
    def get_song_features(self, spotify_url):
        spotify_track_id = TrackService.parse_spotify_track_id(spotify_url)
        reccobeats_track_id = TrackService.get_reccobeats_id(spotify_track_id)

        if reccobeats_track_id is None:
            return None
        
        features_df = self.get_audio_features(reccobeats_track_id)
        details_df = self.get_track_details(reccobeats_track_id)
        
        if features_df is not None and details_df is not None:
            return pd.concat([details_df, features_df], axis=1)
            
        return None