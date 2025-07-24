from yt_dlp import YoutubeDL

def download_media(url: str) -> tuple[str, str]:
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get("title", "video")
