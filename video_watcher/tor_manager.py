"""
Tor integration module for the Video Watcher Automation Tool.
Handles Tor connectivity, identity rotation, and proxy management using Stem library.
"""
import logging
import time
import socket
from typing import Optional, Dict
import requests
from stem import Signal
from stem.control import Controller
from stem.connection import authenticate_none, authenticate_password
from config import Config
from utils import manage_error

logger = logging.getLogger('video_watcher')

class TorManager:
    def __init__(self):
        """Initialize TorManager with configuration from Config class."""
        self.host = Config.TOR_PROXY_HOST
        self.port = Config.TOR_PROXY_PORT
        self.control_port = Config.TOR_CONTROL_PORT
        self.password = Config.TOR_PASSWORD
        self.controller = None
        self._setup_logger()

    def _setup_logger(self):
        """Set up logging for the TorManager class."""
        self.logger = logging.getLogger('video_watcher.tor_manager')

    def start(self) -> bool:
        """
        Start and verify Tor connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to connect to the Tor control port
            self.controller = Controller.from_port(
                address=self.host,
                port=self.control_port
            )
            
            # Authenticate with password if provided, otherwise try no authentication
            if self.password:
                self.controller.authenticate(password=self.password)
            else:
                self.controller.authenticate()

            self.logger.info("Successfully connected to Tor control port")
            return self.validate_tor_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to start Tor connection: {str(e)}")
            manage_error(e, self.logger)
            return False

    def stop(self):
        """Close the Tor controller connection."""
        try:
            if self.controller:
                self.controller.close()
                self.logger.info("Tor controller connection closed")
        except Exception as e:
            self.logger.error(f"Error closing Tor controller: {str(e)}")
            manage_error(e, self.logger)

    def get_new_identity(self) -> bool:
        """
        Request a new Tor identity.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.controller:
                self.logger.error("No active Tor controller connection")
                return False

            # Signal Tor to get a new identity
            self.controller.signal(Signal.NEWNYM)
            self.logger.info("Successfully requested new Tor identity")
            
            # Wait for identity to change (as recommended by Tor)
            time.sleep(self.controller.get_newnym_wait())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to get new Tor identity: {str(e)}")
            manage_error(e, self.logger)
            return False

    def get_proxy_settings(self) -> Dict[str, str]:
        """
        Get proxy settings for use with Selenium.
        
        Returns:
            dict: Proxy settings dictionary
        """
        return {
            'proxy': {
                'http': f'socks5h://{self.host}:{self.port}',
                'https': f'socks5h://{self.host}:{self.port}'
            }
        }

    def validate_tor_connection(self) -> bool:
        """
        Validate Tor connection by making a test request.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Use check.torproject.org to verify Tor connection
            proxies = {
                'http': f'socks5h://{self.host}:{self.port}',
                'https': f'socks5h://{self.host}:{self.port}'
            }
            
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies=proxies,
                timeout=15
            )
            
            if response.status_code == 200 and response.json().get('IsTor', False):
                self.logger.info("Successfully validated Tor connection")
                return True
            else:
                self.logger.warning("Connected to internet but not through Tor")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to validate Tor connection: {str(e)}")
            manage_error(e, self.logger)
            return False

    def get_current_ip(self) -> Optional[str]:
        """
        Get current IP address through Tor network.
        
        Returns:
            str: Current IP address or None if request fails
        """
        try:
            proxies = {
                'http': f'socks5h://{self.host}:{self.port}',
                'https': f'socks5h://{self.host}:{self.port}'
            }
            
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=15
            )
            
            if response.status_code == 200:
                ip = response.json().get('ip')
                self.logger.info(f"Current Tor exit node IP: {ip}")
                return ip
            
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get current IP: {str(e)}")
            manage_error(e, self.logger)
            return None

    def check_tor_service(self) -> bool:
        """
        Check if Tor service is running and accepting connections.
        
        Returns:
            bool: True if Tor service is running, False otherwise
        """
        try:
            # Try to establish a socket connection to the Tor SOCKS port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                self.logger.info("Tor SOCKS service is running")
                return True
            else:
                self.logger.warning("Tor SOCKS service is not running")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking Tor service: {str(e)}")
            manage_error(e, self.logger)
            return False

    def wait_for_tor_service(self, timeout: int = 60, interval: int = 5) -> bool:
        """
        Wait for Tor service to become available.
        
        Args:
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds
            
        Returns:
            bool: True if service becomes available, False if timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_tor_service():
                return True
            time.sleep(interval)
        
        self.logger.error(f"Timeout waiting for Tor service after {timeout} seconds")
        return False