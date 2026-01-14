# import yt_dlp

# def download_video(url, resolution='1080p'):
#     ydl_opts = {
#         'format': f'bestvideo[height<={resolution}]+bestaudio/best',
#         'outtmpl': '%(title)s.%(ext)s',  # Save as video title
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             print(f"Downloading {url} in {resolution} resolution...")
#             ydl.download([url])
#             print("Download complete!")
#     except Exception as e:
#         print(f"An error occurred: {e}")


# video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'  # Replace with your video URL
# download_video(video_url, '1080p')  # Replace '1080p' with your desired resolution

import yt_dlp

def download_video(url, resolution=1080):
    ydl_opts = {
        # Best video up to target resolution + best audio
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',

        # Output file name
        'outtmpl': '%(title)s.%(ext)s',

        # Force MP4 container on merge
        'merge_output_format': 'mp4',

        # Recommended defaults
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading {url} at up to {resolution}p...")
            ydl.download([url])
            print("Download complete! Saved as MP4.")
    except Exception as e:
        print(f"An error occurred: {e}")


video_url = 'https://www.youtube.com/watch?v=8cgWyg8W6UM'
download_video(video_url, 1080)

