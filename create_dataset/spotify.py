import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from flask import Flask, session, url_for, request, redirect
import pandas as pd
import time
from sklearn.preprocessing import MultiLabelBinarizer
import ast

app = Flask(__name__)

load_dotenv(".env")
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
PLAYLIST_NAME = os.getenv("PLAYLIST_NAME")
SCOPE = "playlist-read-private"
CACHE_HANDLER = FlaskSessionCacheHandler(session)
# OUTPUT_PATH = os.getenv("OUTPUT_PATH", "../datasets/main_playlist_tracks.csv")
GENRES = [
    "blues",
    "classical",
    "country",
    "disco",
    "hiphop",
    "jazz",
    "metal",
    "pop",
    "reggae",
    "rock",
]

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


def get_genre(artist_id):
    artist = sp.artist(artist_id)
    genres = artist["genres"]
    return genres if genres else ["Unknown"]


def get_track_info(track):
    if track:
        track_info = {
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
    else:
        track_info = {
            "id": None,
            "name": None,
            "added_at": None,
            "album_id": None,
            "album_name": None,
            "album_imgs": None,
            "artist_id": None,
            "artists_name": None,
            "duration_ms": None,
            "is_explicit": None,
            "popularity": None,
        }

    return track_info


def encode_genres(df):
    # df["genres"] = df.apply(lambda x: [] if "Unknown" in x.genres else x.genres, axis=1)
    # df = df[df["genres"].apply(lambda x: len(x) > 0)]
    df["genres"] = df["genres"].apply(
        lambda x: ast.literal_eval if isinstance(x, str) else x
    )
    mlb = MultiLabelBinarizer()
    one_hot = pd.DataFrame(
        mlb.fit_transform(df["genres"]), columns=mlb.classes_, index=df.index
    )
    one_hot = one_hot.add_prefix("genre_")
    df = pd.concat([df, one_hot], axis=1)
    return df


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
    for i, track in enumerate(playlist_tracks):
        playlist_tracks[i]["genres"] = get_genre(track["artist_id"])
    df = pd.DataFrame(playlist_tracks)
    df["playlist_id"] = playlist_id
    df["playlist_name"] = playlist_name
    df = encode_genres(df)
    df.to_csv("major_playlist_tracks.csv", index=False)
    return playlist_tracks


def get_playlist_tracks(playlist_id):
    playlist_tracks = sp.playlist_tracks(playlist_id, limit=100)
    total_tracks = playlist_tracks["total"]
    print(f"Total tracks in playlist: {total_tracks}")

    playlist_tracks_info = []
    while total_tracks > len(playlist_tracks["items"]):
        print(len(playlist_tracks["items"]))
        next_tracks = sp.playlist_tracks(
            playlist_id, offset=len(playlist_tracks["items"]), limit=100
        )
        playlist_tracks["items"].extend(next_tracks["items"])
        info = [get_track_info(item) for item in next_tracks["items"]]
        try:
            playlist_tracks_info.append(info)
        except Exception as e:
            print(f"Error processing track info: {e}")
            continue
        time.sleep(20)
    return playlist_tracks_info


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
