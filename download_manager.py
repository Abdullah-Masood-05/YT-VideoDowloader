"""
download_manager.py
Manages download queue, threading, and yt-dlp integration
"""

import os
import threading
import queue
import yt_dlp

class DownloadManager:
    """Manages download queue and threading"""
    def __init__(self, callback):
        self.queue = queue.Queue()
        self.callback = callback
        self.active_downloads = {}
        self.download_id = 0
        
    def add_download(self, url, options):
        """Add a download to the queue"""
        self.download_id += 1
        download_info = {
            'id': self.download_id,
            'url': url,
            'options': options,
            'status': 'queued',
            'cancel_flag': threading.Event(),
            'title': 'Unknown'
        }
        self.queue.put(download_info)
        thread = threading.Thread(target=self._process_download, args=(download_info,), daemon=True)
        thread.start()
        return self.download_id
    
    def _process_download(self, download_info):
        """Process a single download"""
        download_id = download_info['id']
        self.active_downloads[download_id] = download_info
        
        try:
            self.callback('status', download_id, 'Starting download...')
            
            # Create progress hook
            def progress_hook(d):
                if download_info['cancel_flag'].is_set():
                    raise Exception("Download cancelled by user")
                    
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%').strip()
                    speed = d.get('_speed_str', 'N/A').strip()
                    eta = d.get('_eta_str', 'N/A').strip()
                    self.callback('progress', download_id, {
                        'percent': percent,
                        'speed': speed,
                        'eta': eta
                    })
                elif d['status'] == 'finished':
                    filename = os.path.basename(d.get('filename', 'Unknown'))
                    self.callback('status', download_id, f"Processing: {filename}")
            
            options = download_info['options'].copy()
            options['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(download_info['url'], download=True)
                
                # Handle playlist or single video
                if 'entries' in info:
                    # It's a playlist
                    title = f"Playlist: {info.get('title', 'Unknown')} ({len(info['entries'])} videos)"
                else:
                    # Single video
                    title = info.get('title', 'Unknown')
                
                download_info['title'] = title
                self.callback('complete', download_id, title)
                
        except Exception as e:
            if download_info['cancel_flag'].is_set():
                self.callback('cancelled', download_id, "Download cancelled")
            else:
                error_msg = str(e)
                # Simplify error messages
                if "ERROR" in error_msg:
                    error_msg = error_msg.split("ERROR:")[-1].strip()
                self.callback('error', download_id, error_msg)
        finally:
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
    
    def cancel_download(self, download_id):
        """Cancel an active download"""
        if download_id in self.active_downloads:
            self.active_downloads[download_id]['cancel_flag'].set()