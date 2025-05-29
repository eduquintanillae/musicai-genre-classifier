import requests
from dotenv import load_dotenv
import os
import base64

load_dotenv(".env")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_song_genre(track_name):
    search_url = f"https://api.spotify.com/v1/search?q={track_name}&type=track&limit=1"
    track_response = requests.get(search_url, headers=HEADERS).json()

    artist_id = track_response["tracks"]["items"][0]["artists"][0]["id"]
    artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    artist_response = requests.get(artist_url, headers=HEADERS).json()
    genres = artist_response["genres"]
    print("Genres:", genres)
    return genres


def get_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    # Request token
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {b64_auth_str}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )

    token = response.json().get("access_token")

    return token


TOKEN = get_token()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
track_name = "Bohemian Rhapsody"
get_song_genre(track_name)
