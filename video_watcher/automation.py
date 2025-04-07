"""
Core automation module for the Video Watcher Automation Tool.
Handles browser automation using Selenium with human-like behavior simulation.
"""
import logging
import random
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
from utils import (
    get_random_user_agent,
    generate_human_like_mouse_movement,
    wait_random_delay,
    should_perform_action,
    manage_error
)

logger = logging.getLogger('video_watcher.automation')

class BrowserAutomation:
    def __init__(self, proxy_settings: dict = None):
        """
        Initialize browser automation with optional proxy settings.
        
        Args:
            proxy_settings: Dictionary containing proxy configuration
        """
        self.proxy_settings = proxy_settings
        self.driver = None
        self.wait = None

    def launch_browser(self) -> bool:
        """
        Launch and configure Chrome browser with appropriate settings.
        
        Returns:
            bool: True if browser launched successfully, False otherwise
        """
        try:
            options = Options()
            
            # Set basic Chrome options
            if Config.HEADLESS_MODE:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-notifications')
            options.add_argument(f'--window-size={Config.DEFAULT_WINDOW_WIDTH},{Config.DEFAULT_WINDOW_HEIGHT}')
            
            # Set random user agent
            user_agent = get_random_user_agent()
            options.add_argument(f'user-agent={user_agent}')
            
            # Configure proxy if provided
            if self.proxy_settings:
                options.add_argument(f'--proxy-server={self.proxy_settings["proxy"]["https"]}')
            
            # Initialize ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("Browser launched successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            manage_error(e, logger)
            return False

    def close_browser(self):
        """Close the browser and clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            manage_error(e, logger)

    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to the specified URL with error handling.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.driver.get(url)
            wait_random_delay(2, 4)  # Wait for page load
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to URL {url}: {str(e)}")
            manage_error(e, logger)
            return False

    def simulate_video_watching(self, url: str, watch_time: Optional[int] = None) -> bool:
        """
        Simulate human-like video watching behavior.
        
        Args:
            url: Video URL to watch
            watch_time: Optional specific watch time in seconds
            
        Returns:
            bool: True if simulation completed successfully, False otherwise
        """
        try:
            if not self.navigate_to_url(url):
                return False

            # Find and interact with video player
            video_element = self._find_video_element()
            if not video_element:
                return False

            # Calculate watch time
            if watch_time is None:
                watch_time = random.randint(Config.MIN_WATCH_TIME, Config.MAX_WATCH_TIME)

            # Start video playback
            self._ensure_video_playing(video_element)
            
            # Simulate watching behavior
            start_time = 0
            while start_time < watch_time:
                # Random interactions during video playback
                if should_perform_action(Config.SCROLL_PROBABILITY):
                    self._perform_random_scroll()
                
                if should_perform_action(Config.CLICK_PROBABILITY):
                    self._perform_random_click()
                
                # Wait for a random interval
                interval = min(random.randint(5, 15), watch_time - start_time)
                wait_random_delay(interval, interval + 2)
                start_time += interval

            logger.info(f"Completed watching video for {watch_time} seconds")
            return True
            
        except Exception as e:
            logger.error("Error during video watching simulation")
            manage_error(e, logger)
            return False

    def _find_video_element(self) -> Optional[webdriver.remote.webelement.WebElement]:
        """Find the video element on the page."""
        try:
            # Try different selectors for video element
            selectors = [
                "video",
                "iframe[src*='youtube']",
                "iframe[src*='vimeo']",
                "#movie_player"
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found video element using selector: {selector}")
                    return element
                except TimeoutException:
                    continue
            
            logger.error("Could not find video element")
            return None
            
        except Exception as e:
            logger.error(f"Error finding video element: {str(e)}")
            manage_error(e, logger)
            return None

    def _ensure_video_playing(self, video_element) -> bool:
        """
        Ensure video is playing by interacting with the player.
        
        Args:
            video_element: The video element to interact with
            
        Returns:
            bool: True if video is playing, False otherwise
        """
        try:
            # Click on video element to focus
            self._simulate_click(video_element)
            wait_random_delay()
            
            # Press space bar to play/pause
            video_element.send_keys(' ')
            wait_random_delay()
            
            logger.info("Video playback initiated")
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring video playback: {str(e)}")
            manage_error(e, logger)
            return False

    def _perform_random_scroll(self):
        """Perform a random scroll action."""
        try:
            scroll_amount = random.randint(-300, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            wait_random_delay()
            logger.debug(f"Performed random scroll: {scroll_amount}px")
            
        except Exception as e:
            logger.error(f"Error performing random scroll: {str(e)}")
            manage_error(e, logger)

    def _perform_random_click(self):
        """Perform a random click on a safe element."""
        try:
            safe_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                'button, .button, .btn, a[href="#"]'
            )
            
            if safe_elements:
                element = random.choice(safe_elements)
                self._simulate_click(element)
                logger.debug("Performed random click on safe element")
                
        except Exception as e:
            logger.error(f"Error performing random click: {str(e)}")
            manage_error(e, logger)

    def _simulate_click(self, element) -> bool:
        """
        Simulate a human-like click on an element.
        
        Args:
            element: The element to click
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            # Get element location and size
            location = element.location
            size = element.size
            
            # Calculate click coordinates (randomly within element)
            click_x = location['x'] + random.randint(5, size['width'] - 5)
            click_y = location['y'] + random.randint(5, size['height'] - 5)
            
            # Generate human-like mouse movement
            current_mouse = self._get_current_mouse_position()
            generate_human_like_mouse_movement(
                self.driver,
                current_mouse,
                (click_x, click_y)
            )
            
            # Perform the click
            element.click()
            wait_random_delay(0.1, 0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Error simulating click: {str(e)}")
            manage_error(e, logger)
            return False

    def _get_current_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position.
        
        Returns:
            tuple: (x, y) coordinates of current mouse position
        """
        try:
            return self.driver.execute_script(
                "return [window.mouseX || 0, window.mouseY || 0];"
            )
        except Exception:
            return (0, 0)  # Fallback to origin if position cannot be determined

    def manage_cookies(self, action: str = 'save') -> bool:
        """
        Manage browser cookies (save or load).
        
        Args:
            action: Either 'save' or 'load'
            
        Returns:
            bool: True if operation successful, False otherwise
        """
        try:
            if action == 'save':
                self.cookies = self.driver.get_cookies()
                logger.info(f"Saved {len(self.cookies)} cookies")
                return True
            elif action == 'load' and hasattr(self, 'cookies'):
                for cookie in self.cookies:
                    self.driver.add_cookie(cookie)
                logger.info(f"Loaded {len(self.cookies)} cookies")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error managing cookies: {str(e)}")
            manage_error(e, logger)
            return False