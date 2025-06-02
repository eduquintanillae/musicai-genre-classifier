import yt_dlp
from dotenv import load_dotenv
import pandas as pd

load_dotenv("../.env")


class YoutubeDL:
    def download(self, urls):
        ydl_opts = {
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
            output_paths = []
            for url in urls:
                info = ydl.extract_info(url, download=False)
                output_paths.append(ydl.prepare_filename(info).replace(".webm", ".wav"))
        return output_paths

    def search_youtube(self, query):
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_term = f"ytsearch:{query}"
            result = ydl.extract_info(search_term, download=False)
            print(result["title"], result["entries"][0]["webpage_url"])
        return result["entries"][0]["webpage_url"]


df = pd.read_csv("../playlist_tracks.csv")
urls = []
for i, row in df.iterrows():
    track_name = row["name"]
    artists_name = row["artists_name"]
    query = f"{track_name} {artists_name}"
    print(query)
    url = YoutubeDL().search_youtube(query)
    print(url)
    urls.append(url)

output_paths = YoutubeDL().download(urls)
df["output_path"] = output_paths
df.to_csv("../playlist_tracks.csv", index=False)
