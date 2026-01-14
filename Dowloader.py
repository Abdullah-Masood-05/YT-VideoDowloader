import yt_dlp

def download_video(url, resolution='1080p'):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',  # Save as video title
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading {url} in {resolution} resolution...")
            ydl.download([url])
            print("Download complete!")
    except Exception as e:
        print(f"An error occurred: {e}")


video_url = 'https://www.youtube.com/watch?v=aGiPeIoSfcw&ab_channel=ImranRiazKhan'
download_video(video_url, '1080p')  # Replace '1080p' with your desired resolution
