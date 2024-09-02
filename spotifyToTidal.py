import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'your_spotify_client_id'
SPOTIPY_CLIENT_SECRET = 'your_spotify_client_secret'
SPOTIPY_REDIRECT_URI = 'your_redirect_uri'

# Tidal API credentials
TIDAL_API_KEY = 'your_tidal_api_key'
TIDAL_API_SECRET = 'your_tidal_api_secret'
TIDAL_ACCESS_TOKEN = 'your_tidal_access_token'  # Get this through Tidal's OAuth process

# Spotify OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="playlist-read-private"))

def get_spotify_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def search_tidal_track(track_name, artist_name):
    url = f'https://api.tidal.com/v1/search/tracks?query={track_name} {artist_name}&limit=1&countryCode=US'
    headers = {
        'Authorization': f'Bearer {TIDAL_ACCESS_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            return data['items'][0]['id']
    return None

def create_tidal_playlist(playlist_name, track_ids):
    url = f'https://api.tidal.com/v1/playlists'
    headers = {
        'Authorization': f'Bearer {TIDAL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'title': playlist_name,
        'description': 'Playlist transferred from Spotify'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        playlist_id = response.json()['uuid']
        add_tracks_to_tidal_playlist(playlist_id, track_ids)
    else:
        print("Error creating Tidal playlist")

def add_tracks_to_tidal_playlist(playlist_id, track_ids):
    url = f'https://api.tidal.com/v1/playlists/{playlist_id}/items'
    headers = {
        'Authorization': f'Bearer {TIDAL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'trackIds': track_ids
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 201:
        print("Tracks added to Tidal playlist")
    else:
        print("Error adding tracks to Tidal playlist")

def transfer_playlist(spotify_playlist_id, tidal_playlist_name):
    spotify_tracks = get_spotify_playlist_tracks(spotify_playlist_id)
    tidal_track_ids = []

    for item in spotify_tracks:
        track_name = item['track']['name']
        artist_name = item['track']['artists'][0]['name']
        tidal_track_id = search_tidal_track(track_name, artist_name)
        if tidal_track_id:
            tidal_track_ids.append(tidal_track_id)

    if tidal_track_ids:
        create_tidal_playlist(tidal_playlist_name, tidal_track_ids)
    else:
        print("No tracks found on Tidal")

# Example usage
spotify_playlist_id = 'your_spotify_playlist_id'
tidal_playlist_name = 'Your Tidal Playlist Name'
transfer_playlist(spotify_playlist_id, tidal_playlist_name)
