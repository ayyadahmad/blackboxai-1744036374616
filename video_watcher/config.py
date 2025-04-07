"""
Configuration settings for the Video Watcher Automation Tool.
Contains default values and settings that can be overridden via environment variables or command line arguments.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # Video watching settings
    TARGET_VIDEO_URL = os.getenv('TARGET_VIDEO_URL', '')
    MIN_WATCH_TIME = int(os.getenv('MIN_WATCH_TIME', '30'))  # minimum watch time in seconds
    MAX_WATCH_TIME = int(os.getenv('MAX_WATCH_TIME', '300'))  # maximum watch time in seconds
    
    # Interaction settings
    MIN_INTERACTION_DELAY = float(os.getenv('MIN_INTERACTION_DELAY', '1.5'))
    MAX_INTERACTION_DELAY = float(os.getenv('MAX_INTERACTION_DELAY', '5.0'))
    SCROLL_PROBABILITY = float(os.getenv('SCROLL_PROBABILITY', '0.3'))
    CLICK_PROBABILITY = float(os.getenv('CLICK_PROBABILITY', '0.2'))
    
    # Tor settings
    TOR_PROXY_HOST = os.getenv('TOR_PROXY_HOST', '127.0.0.1')
    TOR_PROXY_PORT = int(os.getenv('TOR_PROXY_PORT', '9050'))
    TOR_CONTROL_PORT = int(os.getenv('TOR_CONTROL_PORT', '9051'))
    TOR_PASSWORD = os.getenv('TOR_PASSWORD', '')
    
    # Custom proxy settings (optional)
    CUSTOM_PROXY = os.getenv('CUSTOM_PROXY', '')
    
    # Socionator settings
    SOCIONATOR_API_KEY = os.getenv('SOCIONATOR_API_KEY', '')
    SOCIONATOR_API_ENDPOINT = os.getenv('SOCIONATOR_API_ENDPOINT', 'https://api.socionator.com/v1')
    
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
    DEFAULT_WINDOW_WIDTH = int(os.getenv('DEFAULT_WINDOW_WIDTH', '1920'))
    DEFAULT_WINDOW_HEIGHT = int(os.getenv('DEFAULT_WINDOW_HEIGHT', '1080'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'video_watcher.log')
    
    # Web UI settings
    UI_PORT = int(os.getenv('UI_PORT', '8000'))
    UI_HOST = os.getenv('UI_HOST', '0.0.0.0')
    
    @classmethod
    def get_tor_proxy_url(cls):
        """Returns the Tor proxy URL in the format required by Selenium"""
        return f'socks5://{cls.TOR_PROXY_HOST}:{cls.TOR_PROXY_PORT}'
    
    @classmethod
    def get_custom_proxy_url(cls):
        """Returns the custom proxy URL if configured, otherwise None"""
        return cls.CUSTOM_PROXY if cls.CUSTOM_PROXY else None
    
    @classmethod
    def get_window_size(cls):
        """Returns the browser window size as a tuple"""
        return (cls.DEFAULT_WINDOW_WIDTH, cls.DEFAULT_WINDOW_HEIGHT)

    @classmethod
    def is_socionator_enabled(cls):
        """Returns True if Socionator integration is enabled"""
        return bool(cls.SOCIONATOR_API_KEY and cls.SOCIONATOR_API_ENDPOINT)