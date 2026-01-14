"""
config_manager.py
Handles persistent configuration and settings management
"""

import os
import json

class Config:
    """Manages persistent configuration"""
    CONFIG_FILE = "downloader_config.json"
    
    @staticmethod
    def load():
        """Load configuration from file"""
        if os.path.exists(Config.CONFIG_FILE):
            try:
                with open(Config.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_folder': '',
            'theme': 'light',
            'default_resolution': '1080',
            'h264_enabled': False
        }
    
    @staticmethod
    def save(config):
        """Save configuration to file"""
        try:
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")