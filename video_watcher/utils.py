"""
Utility functions for the Video Watcher Automation Tool.
Includes logging setup, random delay generation, and user agent management.
"""
import logging
import random
import time
from typing import Tuple, Optional
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from fake_useragent import UserAgent
from config import Config

def setup_logger() -> logging.Logger:
    """
    Configure and return a logger instance with both file and console handlers.
    """
    logger = logging.getLogger('video_watcher')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    # Create handlers
    file_handler = logging.FileHandler(Config.LOG_FILE)
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_random_user_agent() -> str:
    """
    Generate a random user agent string using fake-useragent library.
    """
    try:
        ua = UserAgent()
        return ua.random
    except Exception as e:
        logger = logging.getLogger('video_watcher')
        logger.warning(f"Failed to generate random user agent: {e}")
        # Fallback to a common user agent if generation fails
        return ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36')

def generate_random_delay(min_delay: float = None, max_delay: float = None) -> float:
    """
    Generate a random delay between min_delay and max_delay seconds.
    Uses Config values if no parameters are provided.
    """
    min_delay = min_delay or Config.MIN_INTERACTION_DELAY
    max_delay = max_delay or Config.MAX_INTERACTION_DELAY
    delay = random.uniform(min_delay, max_delay)
    return delay

def wait_random_delay(min_delay: float = None, max_delay: float = None):
    """
    Sleep for a random amount of time between min_delay and max_delay seconds.
    """
    time.sleep(generate_random_delay(min_delay, max_delay))

def generate_human_like_mouse_movement(
    driver: WebDriver,
    start_coords: Tuple[int, int],
    end_coords: Tuple[int, int],
    steps: int = 25
) -> None:
    """
    Generate smooth, human-like mouse movement between two points using bezier curves.
    
    Args:
        driver: Selenium WebDriver instance
        start_coords: Starting coordinates (x, y)
        end_coords: Ending coordinates (x, y)
        steps: Number of intermediate points to generate
    """
    actions = ActionChains(driver)
    
    # Generate control points for bezier curve
    control_point1 = (
        start_coords[0] + random.randint(-100, 100),
        start_coords[1] + random.randint(-100, 100)
    )
    control_point2 = (
        end_coords[0] + random.randint(-100, 100),
        end_coords[1] + random.randint(-100, 100)
    )
    
    points = _generate_bezier_curve(
        start_coords,
        control_point1,
        control_point2,
        end_coords,
        steps
    )
    
    # Move through each point with small random delays
    for point in points:
        actions.move_by_offset(point[0], point[1])
        actions.pause(random.uniform(0.001, 0.003))
    
    actions.perform()

def _generate_bezier_curve(
    p0: Tuple[int, int],
    p1: Tuple[int, int],
    p2: Tuple[int, int],
    p3: Tuple[int, int],
    steps: int
) -> list:
    """
    Generate points along a cubic bezier curve.
    """
    points = []
    for t in range(steps):
        t = t / steps
        
        # Cubic bezier formula
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + \
            3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + \
            3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        
        points.append((int(x), int(y)))
    
    return points

def should_perform_action(probability: float) -> bool:
    """
    Determine if an action should be performed based on its probability.
    
    Args:
        probability: Float between 0 and 1 representing the probability
    Returns:
        bool: True if action should be performed, False otherwise
    """
    return random.random() < probability

def manage_error(error: Exception, logger: Optional[logging.Logger] = None) -> None:
    """
    Handle and log errors appropriately.
    
    Args:
        error: The exception that occurred
        logger: Optional logger instance. If not provided, creates a new one.
    """
    if logger is None:
        logger = logging.getLogger('video_watcher')
    
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.error(f"Error occurred: {error_type} - {error_message}")
    logger.debug(f"Error details:", exc_info=True)