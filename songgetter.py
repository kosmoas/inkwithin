import yt_dlp
def search_and_download(search_query):
   ydl_opts = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "outtmpl": "-", 
}
   with yt_dlp.YoutubeDL(ydl_opts) as ydl:
           info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
           url = info["entries"][0]["url"]
           print("Streaming URL:", url)
   return url