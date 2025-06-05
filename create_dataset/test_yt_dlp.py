import yt_dlp
from dotenv import load_dotenv
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import time
import os

load_dotenv("../.env")


class YoutubeDL:
    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio/best",
            "ffmpeg_location": "C:/Users/Edu/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin",
            "outtmpl": "C:../audios/%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }

    def search_youtube(self, query):
        with yt_dlp.YoutubeDL({}) as ydl:
            search_term = f"ytsearch:{query}"
            result = ydl.extract_info(search_term, download=False)
        return result["entries"][0]["webpage_url"]

    def download_single(self, url):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            return ydl.prepare_filename(info).replace(".webm", ".wav")


# Function to search a single track
def search_track(row):
    ydl = YoutubeDL()
    track_name = row["name"]
    artists_name = row["artists_name"]
    query = f"{track_name} {artists_name}"
    return ydl.search_youtube(query)


# Function to download a single track
def download_url(url):
    ydl = YoutubeDL()
    return ydl.download_single(url)


if __name__ == "__main__":
    start_time = time.time()
    dataset_path = "../datasets/playlist_tracks.csv"
    df = pd.read_csv(dataset_path)

    with ProcessPoolExecutor() as executor:
        urls = list(executor.map(search_track, [row for _, row in df.iterrows()]))

    df["youtube_url"] = urls

    with ProcessPoolExecutor() as executor:
        output_paths = list(executor.map(download_url, urls))

    df["output_path"] = output_paths
    df.to_csv(dataset_path, index=False)
    end_time = time.time()
    print(
        f"Downloaded {len(output_paths)} tracks in {end_time - start_time:.2f} seconds."
    )
