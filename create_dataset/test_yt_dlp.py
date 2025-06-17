import yt_dlp
from dotenv import load_dotenv
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

load_dotenv("../.env")
FOLDER = "../datasets/audios/major_playlist"


class YoutubeDL:
    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio/best",
            "ffmpeg_location": "C:/Users/Edu/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin",
            "outtmpl": f"C:{FOLDER}/%(title)s.%(ext)s",
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


def search_track(row):
    ydl = YoutubeDL()
    track_name = row.name
    artists_name = row.artists_name
    query = f"{track_name} {artists_name}"
    try:
        url = ydl.search_youtube(query)
    except Exception as e:
        url = None
    return url


def download_url(url):
    ydl = YoutubeDL()
    if url:
        return ydl.download_single(url)
    else:
        print("No URL found for this track.")
        return None


if __name__ == "__main__":
    start_time = time.time()
    dataset_path = "../datasets/major_playlist_tracks.csv"
    chunk_size = 500
    output_path = f"{dataset_path}"

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset with shape: {df.shape}")

    final_df_chunks = []
    for i in tqdm(range(0, len(df), chunk_size), desc="Processing chunks"):
        j = min(i + chunk_size, len(df))
        print(f"Processing rows {i} to {j}...")

        df_subset = df.iloc[i:j].copy()
        with ThreadPoolExecutor() as executor:
            urls = list(executor.map(search_track, df_subset.itertuples(index=False)))
            df_subset["youtube_url"] = urls
            output_paths = list(executor.map(download_url, urls))
            df_subset["output_path"] = output_paths
        final_df_chunks.append(df_subset)

    final_df = pd.concat(final_df_chunks, ignore_index=True)
    final_df.to_csv(output_path, index=False)
    total_time = time.time() - start_time
    print(f"Processed in {total_time:.2f} seconds.")
    print(f"Saved processed dataset to {output_path}")
