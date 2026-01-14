import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import subprocess

# Import our modules
from config_manager import Config
from download_manager import DownloadManager

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader Pro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configuration
        self.config = Config.load()
        self.current_theme = self.config.get('theme', 'light')
        
        # Download manager
        self.download_manager = DownloadManager(self.download_callback)
        self.active_download_widgets = {}
        
        # Check FFmpeg
        self.ffmpeg_available = self.check_ffmpeg()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.apply_theme()
        self.bind_shortcuts()
        
        # Load history after GUI is ready
        self.root.after(100, self.load_history_panel)
        
        # Enable clipboard detection
        self.setup_clipboard_detection()
        
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
            return True
        except:
            return False
    
    def setup_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        
        # Configure button styles
        self.style.configure('Download.TButton', padding=10, font=('Segoe UI', 10, 'bold'))
        self.style.configure('Action.TButton', padding=5, font=('Segoe UI', 9))
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Section.TLabel', font=('Segoe UI', 10, 'bold'))
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Input Section
        self.create_input_section(main_frame)
        
        # Options Section
        self.create_options_section(main_frame)
        
        # Action Buttons
        self.create_action_buttons(main_frame)
        
        # Notebook for tabs
        self.create_tabbed_area(main_frame)
        
    def create_header(self, parent):
        """Create header with title and theme toggle"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        title = ttk.Label(header_frame, text="YouTube Video Downloader Pro", 
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky=tk.W)
        
        # Theme toggle button
        theme_btn = ttk.Button(header_frame, text="🌓 Toggle Theme", 
                              command=self.toggle_theme, style='Action.TButton')
        theme_btn.grid(row=0, column=2, padx=5)
        
        # FFmpeg status
        ffmpeg_status = "✓ FFmpeg detected" if self.ffmpeg_available else "⚠ FFmpeg not found"
        ffmpeg_color = "green" if self.ffmpeg_available else "orange"
        self.ffmpeg_label = tk.Label(header_frame, text=ffmpeg_status, 
                                     fg=ffmpeg_color, font=('Segoe UI', 9))
        self.ffmpeg_label.grid(row=0, column=3, padx=5)
        
    def create_input_section(self, parent):
        """Create URL input section"""
        input_frame = ttk.LabelFrame(parent, text="Video URL", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        # URL entry
        url_container = ttk.Frame(input_frame)
        url_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        url_container.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_container, font=('Segoe UI', 10))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Tooltip label
        tooltip = ttk.Label(input_frame, 
                           text="💡 Paste YouTube video or playlist URL. Press Enter to start download.",
                           font=('Segoe UI', 8))
        tooltip.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
    def create_options_section(self, parent):
        """Create options section"""
        options_frame = ttk.LabelFrame(parent, text="Download Options", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        options_frame.columnconfigure(1, weight=1)
        
        # Resolution
        ttk.Label(options_frame, text="Max Resolution:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.resolution_var = tk.StringVar(value=self.config.get('default_resolution', '1080'))
        resolution_combo = ttk.Combobox(options_frame, textvariable=self.resolution_var, 
                                       values=['360', '480', '720', '1080', '1440', '2160'], 
                                       width=10, state='readonly')
        resolution_combo.grid(row=0, column=1, sticky=tk.W)
        ttk.Label(options_frame, text="p", font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W)
        
        # H.264 codec
        self.h264_var = tk.BooleanVar(value=self.config.get('h264_enabled', False))
        h264_check = ttk.Checkbutton(options_frame, text="Force H.264 codec", 
                                     variable=self.h264_var)
        h264_check.grid(row=0, column=3, sticky=tk.W, padx=(20, 0))
        
        # Tooltip for H.264
        h264_tooltip = ttk.Label(options_frame, 
                                text="(Better compatibility with older devices)",
                                font=('Segoe UI', 8))
        h264_tooltip.grid(row=0, column=4, sticky=tk.W, padx=(5, 0))
        
        # Output folder
        ttk.Label(options_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        folder_frame = ttk.Frame(options_frame)
        folder_frame.grid(row=1, column=1, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        folder_frame.columnconfigure(0, weight=1)
        
        self.output_dir = tk.StringVar(value=self.config.get('last_folder', ''))
        folder_entry = ttk.Entry(folder_frame, textvariable=self.output_dir, font=('Segoe UI', 9))
        folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(folder_frame, text="Browse", 
                               command=self.browse_folder, style='Action.TButton')
        browse_btn.grid(row=0, column=1)
        
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, pady=10)
        
        # Download button
        self.download_btn = ttk.Button(button_frame, text="⬇ Download", 
                                      command=self.start_download, 
                                      style='Download.TButton')
        self.download_btn.grid(row=0, column=0, padx=5)
        
        # Clear log button
        clear_btn = ttk.Button(button_frame, text="🗑 Clear Log", 
                              command=self.clear_log, style='Action.TButton')
        clear_btn.grid(row=0, column=1, padx=5)
        
    def create_tabbed_area(self, parent):
        """Create notebook with tabs for downloads and history"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        # Downloads tab
        downloads_tab = ttk.Frame(self.notebook)
        self.notebook.add(downloads_tab, text="📥 Downloads")
        
        # Create scrollable frame for downloads
        downloads_canvas = tk.Canvas(downloads_tab, highlightthickness=0)
        downloads_scrollbar = ttk.Scrollbar(downloads_tab, orient="vertical", 
                                           command=downloads_canvas.yview)
        self.downloads_frame = ttk.Frame(downloads_canvas)
        
        self.downloads_frame.bind(
            "<Configure>",
            lambda e: downloads_canvas.configure(scrollregion=downloads_canvas.bbox("all"))
        )
        
        downloads_canvas.create_window((0, 0), window=self.downloads_frame, anchor="nw")
        downloads_canvas.configure(yscrollcommand=downloads_scrollbar.set)
        
        downloads_canvas.pack(side="left", fill="both", expand=True)
        downloads_scrollbar.pack(side="right", fill="y")
        
        # Store canvas reference for theme switching
        self.downloads_canvas = downloads_canvas
        
        # Log tab
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="📋 Log")
        
        self.log_area = scrolledtext.ScrolledText(log_tab, wrap=tk.WORD, 
                                                  font=('Consolas', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # History tab
        history_tab = ttk.Frame(self.notebook)
        self.notebook.add(history_tab, text="📜 History")
        
        self.history_area = scrolledtext.ScrolledText(history_tab, wrap=tk.WORD, 
                                                      font=('Consolas', 9), state='normal')
        self.history_area.pack(fill=tk.BOTH, expand=True)
        
    def setup_clipboard_detection(self):
        """Setup basic clipboard detection for URLs"""
        self.url_entry.bind('<Control-v>', self.on_paste)
        self.url_entry.bind('<<Paste>>', self.on_paste)
        
    def on_paste(self, event=None):
        """Handle paste event"""
        self.root.after(50, self._check_pasted_content)
        
    def _check_pasted_content(self):
        """Check if pasted content is a YouTube URL"""
        try:
            content = self.url_entry.get()
            if 'youtube.com' in content or 'youtu.be' in content:
                self.log_message(f"✓ URL detected from clipboard")
        except:
            pass
        
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind('<Return>', lambda e: self.start_download())
        self.root.bind('<Control-l>', lambda e: self.clear_log())
        self.root.bind('<Control-L>', lambda e: self.clear_log())
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == 'light':
            self.current_theme = 'dark'
        else:
            self.current_theme = 'light'
        
        self.config['theme'] = self.current_theme
        Config.save(self.config)
        self.apply_theme()
        
    def apply_theme(self):
        """Apply color theme to all widgets"""
        if self.current_theme == 'dark':
            # Dark theme colors
            root_bg = '#2b2b2b'
            canvas_bg = '#1e1e1e'
            text_bg = '#1e1e1e'
            text_fg = '#d4d4d4'
            frame_bg = '#2b2b2b'
        else:
            # Light theme colors
            root_bg = '#f0f0f0'
            canvas_bg = '#ffffff'
            text_bg = '#ffffff'
            text_fg = '#000000'
            frame_bg = '#f0f0f0'
        
        # Apply to root window
        self.root.configure(bg=root_bg)
        
        # Apply to text areas
        self.log_area.configure(bg=text_bg, fg=text_fg, insertbackground=text_fg)
        self.history_area.configure(bg=text_bg, fg=text_fg, insertbackground=text_fg)
        
        # Apply to downloads canvas
        if hasattr(self, 'downloads_canvas'):
            self.downloads_canvas.configure(bg=canvas_bg)
            
        # Apply to downloads frame
        if hasattr(self, 'downloads_frame'):
            self.downloads_frame.configure(style='TFrame')
            
        # Update ttk theme for better dark mode support
        if self.current_theme == 'dark':
            try:
                self.style.theme_use('clam')  # Use clam theme for better dark mode
            except:
                pass
        
    def browse_folder(self):
        """Open folder browser"""
        folder = filedialog.askdirectory(initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)
            self.config['last_folder'] = folder
            Config.save(self.config)
            
    def start_download(self):
        """Start download process"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not self.ffmpeg_available:
            response = messagebox.askyesno(
                "FFmpeg Not Found",
                "FFmpeg is not detected. Video merging may fail.\n\n"
                "Do you want to continue anyway?"
            )
            if not response:
                return
        
        try:
            resolution = int(self.resolution_var.get())
        except:
            resolution = 1080
        
        output_dir_val = self.output_dir.get() or None
        h264_val = self.h264_var.get()
        
        # Build yt-dlp options
        outtmpl = '%(title)s.%(ext)s'
        if output_dir_val:
            os.makedirs(output_dir_val, exist_ok=True)
            outtmpl = os.path.join(output_dir_val, outtmpl)
        
        ydl_opts = {
            'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best',
            'merge_output_format': 'mp4',
            'outtmpl': outtmpl,
            'noplaylist': False,
        }
        
        if h264_val:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        
        # Save config
        self.config['default_resolution'] = self.resolution_var.get()
        self.config['h264_enabled'] = h264_val
        Config.save(self.config)
        
        # Add to download queue
        download_id = self.download_manager.add_download(url, ydl_opts)
        self.create_download_widget(download_id, url)
        
        # Log
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_message(f"[{timestamp}] Added to queue: {url}")
        
        # Save to history (will be updated when download completes)
        self.pending_history = {
            'url': url,
            'resolution': resolution,
            'h264': h264_val,
            'download_id': download_id
        }
        
    def create_download_widget(self, download_id, url):
        """Create a widget for tracking download progress"""
        frame = ttk.LabelFrame(self.downloads_frame, text=f"Download #{download_id}", 
                              padding="10")
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL label (truncated)
        url_display = url[:80] + "..." if len(url) > 80 else url
        url_label = ttk.Label(frame, text=url_display, font=('Segoe UI', 9))
        url_label.pack(anchor=tk.W)
        
        # Progress bar
        progress_bar = ttk.Progressbar(frame, length=400, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(5, 0))
        progress_bar.start(10)
        
        # Status label
        status_label = ttk.Label(frame, text="Initializing...", font=('Segoe UI', 9))
        status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Cancel button
        cancel_btn = ttk.Button(frame, text="Cancel", 
                               command=lambda: self.cancel_download(download_id),
                               style='Action.TButton')
        cancel_btn.pack(anchor=tk.E, pady=(5, 0))
        
        self.active_download_widgets[download_id] = {
            'frame': frame,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'cancel_btn': cancel_btn
        }
        
        # Switch to downloads tab
        self.notebook.select(0)
        
    def cancel_download(self, download_id):
        """Cancel a download"""
        self.download_manager.cancel_download(download_id)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_message(f"[{timestamp}] Cancelled download #{download_id}")
        
    def download_callback(self, event_type, download_id, data):
        """Callback for download events"""
        self.root.after(0, self._update_download_widget, event_type, download_id, data)
        
    def _update_download_widget(self, event_type, download_id, data):
        """Update download widget (must run in main thread)"""
        if download_id not in self.active_download_widgets:
            return
        
        widget = self.active_download_widgets[download_id]
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if event_type == 'progress':
            percent_str = data['percent'].replace('%', '')
            try:
                percent = float(percent_str)
                widget['progress_bar'].stop()
                widget['progress_bar'].configure(mode='determinate', value=percent)
            except:
                pass
            status_text = f"⬇ {data['percent']} | Speed: {data['speed']} | ETA: {data['eta']}"
            widget['status_label'].configure(text=status_text)
            
        elif event_type == 'status':
            widget['status_label'].configure(text=data)
            
        elif event_type == 'complete':
            widget['progress_bar'].stop()
            widget['progress_bar'].configure(value=100)
            widget['status_label'].configure(text=f"✓ Completed: {data}")
            widget['cancel_btn'].configure(text="Close", 
                                          command=lambda: self.remove_download_widget(download_id))
            self.log_message(f"[{timestamp}] Completed: {data}")
            
            # Save to history with video title
            if hasattr(self, 'pending_history') and self.pending_history['download_id'] == download_id:
                self.save_to_history(
                    self.pending_history['url'],
                    self.pending_history['resolution'],
                    self.pending_history['h264'],
                    data  # video title
                )
                # Reload history panel
                self.root.after(100, self.load_history_panel)
            
        elif event_type == 'error':
            widget['progress_bar'].stop()
            widget['status_label'].configure(text=f"✗ Error: {data}")
            widget['cancel_btn'].configure(text="Close", 
                                          command=lambda: self.remove_download_widget(download_id))
            self.log_message(f"[{timestamp}] Error in download #{download_id}: {data}")
            
        elif event_type == 'cancelled':
            widget['progress_bar'].stop()
            widget['status_label'].configure(text="✗ Cancelled")
            widget['cancel_btn'].configure(text="Close", 
                                          command=lambda: self.remove_download_widget(download_id))
            
    def remove_download_widget(self, download_id):
        """Remove download widget"""
        if download_id in self.active_download_widgets:
            self.active_download_widgets[download_id]['frame'].destroy()
            del self.active_download_widgets[download_id]
            
    def log_message(self, message):
        """Add message to log"""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        
    def clear_log(self):
        """Clear the log area"""
        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_area.insert(tk.END, f"[{timestamp}] Log cleared\n")
        self.log_area.configure(state='disabled')
        
    def save_to_history(self, url, resolution, h264, title="Unknown"):
        """Save download to history file"""
        try:
            with open("download_history.log", "a", encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {title}\n")
                f.write(f"  URL: {url}\n")
                f.write(f"  Resolution: {resolution}p | H264: {h264}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            print(f"Error saving to history: {e}")
        
    def load_history_panel(self):
        """Load history into the history tab"""
        self.history_area.configure(state='normal')
        self.history_area.delete('1.0', tk.END)
        
        if os.path.exists("download_history.log"):
            try:
                with open("download_history.log", "r", encoding='utf-8') as f:
                    history = f.read()
                    if history.strip():
                        self.history_area.insert('1.0', history)
                    else:
                        self.history_area.insert('1.0', "No download history yet.\n\nCompleted downloads will appear here.")
            except Exception as e:
                self.history_area.insert('1.0', f"Unable to load history: {e}")
        else:
            self.history_area.insert('1.0', "No download history yet.\n\nCompleted downloads will appear here.")
        
        self.history_area.configure(state='disabled')

# -------------------------------
# Main Entry Point
# -------------------------------
def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()