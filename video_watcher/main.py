"""
Main entry point for the Video Watcher Automation Tool.
Coordinates all components and provides the core functionality.
"""
import argparse
import logging
import sys
import time
from typing import Optional, Dict, Any
from config import Config
from utils import setup_logger
from tor_manager import TorManager
from automation import BrowserAutomation
from socionator_integration import SocionatorAPI

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Video Watcher Automation Tool with Tor integration'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        help='URL of the video to watch'
    )
    
    parser.add_argument(
        '--watch-time',
        type=int,
        help='Specific watch time in seconds (overrides random)'
    )
    
    parser.add_argument(
        '--custom-proxy',
        type=str,
        help='Custom proxy URL (overrides Tor)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

class VideoWatcher:
    def __init__(self, args: argparse.Namespace):
        """
        Initialize VideoWatcher with command line arguments.
        
        Args:
            args: Parsed command line arguments
        """
        self.args = args
        self.logger = setup_logger()
        if args.debug:
            self.logger.setLevel(logging.DEBUG)
        
        self.tor_manager = None
        self.browser = None
        self.socionator = None
        self.session_data = {
            'start_time': None,
            'interactions': {
                'clicks': 0,
                'scrolls': 0,
                'pauses': 0
            }
        }

    def initialize_components(self) -> bool:
        """
        Initialize all required components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Initialize Tor if no custom proxy specified
            if not self.args.custom_proxy:
                self.tor_manager = TorManager()
                if not self.tor_manager.start():
                    self.logger.error("Failed to initialize Tor connection")
                    return False
                proxy_settings = self.tor_manager.get_proxy_settings()
            else:
                proxy_settings = {
                    'proxy': {
                        'http': self.args.custom_proxy,
                        'https': self.args.custom_proxy
                    }
                }

            # Initialize browser automation
            self.browser = BrowserAutomation(proxy_settings)
            if not self.browser.launch_browser():
                self.logger.error("Failed to launch browser")
                return False

            # Initialize Socionator if enabled
            if Config.is_socionator_enabled():
                self.socionator = SocionatorAPI()
                if not self.socionator.initialize():
                    self.logger.warning("Failed to initialize Socionator API")
                    # Continue anyway as Socionator is optional

            return True

        except Exception as e:
            self.logger.error(f"Error during initialization: {str(e)}")
            return False

    def run_session(self) -> bool:
        """
        Run a complete video watching session.
        
        Returns:
            bool: True if session completed successfully, False otherwise
        """
        try:
            self.session_data['start_time'] = int(time.time())
            
            # Get video URL from args or config
            video_url = self.args.url or Config.TARGET_VIDEO_URL
            if not video_url:
                self.logger.error("No video URL provided")
                return False

            # Start watch session
            self.logger.info(f"Starting watch session for: {video_url}")
            
            # Send initial event to Socionator
            if self.socionator:
                self.socionator.send_engagement_event(
                    'session_start',
                    video_url,
                    {'proxy_type': 'tor' if self.tor_manager else 'custom'}
                )

            # Simulate video watching
            success = self.browser.simulate_video_watching(
                video_url,
                self.args.watch_time
            )

            if success:
                self.logger.info("Watch session completed successfully")
                self._report_session_completion(video_url)
                return True
            else:
                self.logger.error("Watch session failed")
                self._report_session_error(video_url, "Simulation failed")
                return False

        except Exception as e:
            self.logger.error(f"Error during watch session: {str(e)}")
            if video_url and self.socionator:
                self._report_session_error(video_url, str(e))
            return False

    def _report_session_completion(self, video_url: str):
        """Report successful session completion to Socionator."""
        if self.socionator:
            watch_time = int(time.time()) - self.session_data['start_time']
            self.socionator.send_watch_session(
                video_url,
                watch_time,
                self.session_data['interactions'],
                'tor' if self.tor_manager else self.args.custom_proxy
            )

    def _report_session_error(self, video_url: str, error_message: str):
        """Report session error to Socionator."""
        if self.socionator:
            self.socionator.send_engagement_event(
                'session_error',
                video_url,
                {'error': error_message}
            )

    def cleanup(self):
        """Clean up resources and close connections."""
        try:
            if self.browser:
                self.browser.close_browser()
            
            if self.tor_manager:
                self.tor_manager.stop()
            
            if self.socionator:
                self.socionator.close()
                
            self.logger.info("Cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    watcher = VideoWatcher(args)
    
    try:
        if watcher.initialize_components():
            success = watcher.run_session()
            if success:
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        watcher.logger.info("Received keyboard interrupt, shutting down...")
        sys.exit(0)
        
    except Exception as e:
        watcher.logger.error(f"Unhandled error: {str(e)}")
        sys.exit(1)
        
    finally:
        watcher.cleanup()

if __name__ == '__main__':
    main()