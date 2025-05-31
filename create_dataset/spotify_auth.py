import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, request, redirect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

load_dotenv(".env")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
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
    validate_token()
    playlists = sp.current_user_playlists()
    playlist_id = playlists["items"][0]["id"]
    playlist_tracks = sp.playlist_tracks(playlist_id)
    playlist_tracks = [get_track_info(item) for item in playlist_tracks["items"]]
    return playlist_tracks


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
