import yt_dlp


class YoutubeDL:
    def __init__(self):
        self.ydl_opts = {
            "format": "bestaudio/best",
            "ffmpeg_location": "C:/Users/Edu/Downloads/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin",
            "outtmpl": "C:./audios/%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }

    def download(self, urls):
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download(urls)


YoutubeDL().download(["https://www.youtube.com/watch?v=XJBrrOarTfs"])
