import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, request, redirect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

##SETTING UP AUTHENTICATION

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

##CREATE INSTANCE OF SPOTIFY CLIENT
sp = Spotify(auth_manager=sp_oauth)
##ENDPOINTS


def validate_token():
    if not sp_oauth.validate_token(CACHE_HANDLER.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)


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
    print("Playlist ID:", playlist_id)
    playlist_tracks = sp.playlist_tracks(playlist_id)
    return {"playlist": playlists["items"][0], "tracks": playlist_tracks}


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
