import librosa
import pandas as pd

folder_path = "../playlist_tracks_with_urls.csv"
df = pd.read_csv(folder_path)
df["output_path"] = df.apply(
    lambda x: x.output_path.replace(".webm", ".wav")
    .replace("C:", "")
    .replace("\\", "/"),
    axis=1,
)


def analyze_audio(file_path):
    print(f"Processing {file_path}...")
    y, sr = librosa.load(file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo


for index, row in df.iterrows():
    file_path = row["output_path"]
    tempo = analyze_audio(file_path)
    if tempo:
        df.at[index, "tempo"] = tempo
df.to_csv(folder_path, index=False)
