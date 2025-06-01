import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, request, redirect
import pandas as pd

app = Flask(__name__)

load_dotenv(".env")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
PLAYLIST_NAME = os.getenv("PLAYLIST_NAME")
SCOPE = "playlist-read-private"
CACHE_HANDLER = FlaskSessionCacheHandler(session)

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_handler=CACHE_HANDLER,
    show_dialog=True,
)
sp = Spotify(auth_manager=sp_oauth)


def validate_token():
    if not sp_oauth.validate_token(CACHE_HANDLER.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)


def get_track_info(track):
    return {
        "id": track["track"]["id"],
        "name": track["track"]["name"],
        "added_at": track["added_at"],
        "album_id": track["track"]["album"]["id"],
        "album_name": track["track"]["album"]["name"],
        "album_imgs": track["track"]["album"]["images"],
        "artist_id": track["track"]["artists"][0]["id"],
        "artists_name": track["track"]["artists"][0]["name"],
        "duration_ms": track["track"]["duration_ms"],
        "is_explicit": track["track"]["explicit"],
        "popularity": track["track"]["popularity"],
    }


@app.route("/")
def home():
    validate_token()
    return redirect(url_for("get_playlists"))


@app.route("/callback")
def callback():
    sp_oauth.get_access_token(request.args["code"])
    return redirect(url_for("get_playlists"))


@app.route("/get_playlists")
def get_playlists():
    playlists = sp.current_user_playlists()
    playlist_id = None
    playlist_name = PLAYLIST_NAME
    for playlist in playlists["items"]:
        if playlist["name"] == playlist_name:
            playlist_id = playlist["id"]
            break
    if not playlist_id:
        return "Playlist not found. Please provide a valid playlist name."
    playlist_tracks = get_playlist_tracks(playlist_id)
    df = pd.DataFrame(playlist_tracks)
    df["playlist_id"] = playlist_id
    df["playlist_name"] = playlists["items"][0]["name"]
    df.to_csv("playlist_tracks.csv", index=False)
    return playlist_tracks


def get_playlist_tracks(playlist_id):
    playlist_tracks = sp.playlist_tracks(playlist_id)
    playlist_tracks = [get_track_info(item) for item in playlist_tracks["items"]]
    return playlist_tracks


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
