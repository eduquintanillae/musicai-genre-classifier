import librosa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

folder_path = "../datasets/playlist_tracks.csv"
df = pd.read_csv(folder_path)
df["output_path"] = df.apply(
    lambda x: x.output_path.replace(".webm", ".wav")
    .replace("C:", "")
    .replace("\\", "/"),
    axis=1,
)


def get_tempo(file_path):
    y, sr = librosa.load(file_path, sr=None)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return tempo, sr


def get_mel_spectrogram(file_path):
    y, sr = librosa.load(file_path, sr=None)
    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
    print(f"Processed {file_path} with shape {mel_spectrogram_db.shape}")
    return mel_spectrogram_db


for index, row in df.iterrows():
    file_path = row["output_path"]
    file_name = Path(row["output_path"]).name.replace(".wav", "")
    print(f"--- Processing '{file_name}' ---")

    tempo, sr = get_tempo(file_path)
    print(f"Tempo: {tempo} BPM, Sample Rate: {sr} Hz")
    if tempo:
        df.at[index, "tempo"] = tempo

    mel_spectrogram = get_mel_spectrogram(file_path)

    img_size = (224, 224)
    plt.figure(figsize=(img_size[0] / 100, img_size[1] / 100), dpi=100)
    librosa.display.specshow(
        mel_spectrogram, sr=sr, x_axis=None, y_axis=None, cmap="magma"
    )
    plt.axis("off")
    plt.tight_layout(pad=0)
    output_path = Path(f"../datasets/images/mel_spectrograms/{file_name}.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, bbox_inches="tight", pad_inches=0)
    plt.close()

df.to_csv(folder_path, index=False)
