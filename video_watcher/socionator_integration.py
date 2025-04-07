"""
Socionator API integration module for the Video Watcher Automation Tool.
Handles sending engagement metrics and events to the Socionator platform.
"""
import logging
import json
import time
from typing import Dict, Any, Optional
import requests
from requests.exceptions import RequestException
from config import Config
from utils import manage_error

logger = logging.getLogger('video_watcher.socionator')

class SocionatorAPI:
    def __init__(self):
        """Initialize Socionator API client with configuration."""
        self.api_key = Config.SOCIONATOR_API_KEY
        self.api_endpoint = Config.SOCIONATOR_API_ENDPOINT
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'VideoWatcher/1.0'
        })

    def initialize(self) -> bool:
        """
        Initialize connection with Socionator API.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not self.api_key or not self.api_endpoint:
            logger.error("Socionator API key or endpoint not configured")
            return False

        try:
            response = self.session.get(f'{self.api_endpoint}/status')
            if response.status_code == 200:
                logger.info("Successfully connected to Socionator API")
                return True
            else:
                logger.error(f"Failed to connect to Socionator API: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error initializing Socionator API: {str(e)}")
            manage_error(e, logger)
            return False

    def send_engagement_event(
        self,
        event_type: str,
        video_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send an engagement event to Socionator.
        
        Args:
            event_type: Type of engagement event (e.g., 'view', 'interaction')
            video_url: URL of the video being watched
            metadata: Additional metadata about the event
            
        Returns:
            bool: True if event was sent successfully, False otherwise
        """
        if not self.api_key:
            logger.error("Socionator API key not configured")
            return False

        try:
            payload = {
                'event_type': event_type,
                'video_url': video_url,
                'timestamp': int(time.time()),
                'metadata': metadata or {}
            }

            response = self.session.post(
                f'{self.api_endpoint}/events',
                json=payload
            )

            if response.status_code == 201:
                logger.info(f"Successfully sent {event_type} event to Socionator")
                return True
            else:
                logger.error(
                    f"Failed to send event to Socionator: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending event to Socionator: {str(e)}")
            manage_error(e, logger)
            return False

    def send_watch_session(
        self,
        video_url: str,
        watch_time: int,
        interactions: Dict[str, int],
        proxy_used: Optional[str] = None
    ) -> bool:
        """
        Send a complete watch session report to Socionator.
        
        Args:
            video_url: URL of the watched video
            watch_time: Total watch time in seconds
            interactions: Dictionary of interaction counts
            proxy_used: Proxy information (if applicable)
            
        Returns:
            bool: True if session was reported successfully, False otherwise
        """
        try:
            payload = {
                'video_url': video_url,
                'watch_time': watch_time,
                'interactions': interactions,
                'proxy_info': proxy_used,
                'timestamp': int(time.time())
            }

            response = self.session.post(
                f'{self.api_endpoint}/sessions',
                json=payload
            )

            if response.status_code == 201:
                logger.info("Successfully reported watch session to Socionator")
                return True
            else:
                logger.error(
                    f"Failed to report session to Socionator: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error reporting session to Socionator: {str(e)}")
            manage_error(e, logger)
            return False

    def get_engagement_metrics(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve engagement metrics for a specific video.
        
        Args:
            video_url: URL of the video to get metrics for
            
        Returns:
            dict: Engagement metrics if successful, None otherwise
        """
        try:
            response = self.session.get(
                f'{self.api_endpoint}/metrics',
                params={'video_url': video_url}
            )

            if response.status_code == 200:
                metrics = response.json()
                logger.info("Successfully retrieved engagement metrics")
                return metrics
            else:
                logger.error(
                    f"Failed to get metrics from Socionator: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Error getting metrics from Socionator: {str(e)}")
            manage_error(e, logger)
            return None

    def update_session_status(
        self,
        session_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update the status of a watch session.
        
        Args:
            session_id: ID of the session to update
            status: New status value
            error_message: Optional error message if status is 'error'
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            payload = {
                'status': status,
                'error_message': error_message
            }

            response = self.session.patch(
                f'{self.api_endpoint}/sessions/{session_id}',
                json=payload
            )

            if response.status_code == 200:
                logger.info(f"Successfully updated session {session_id} status")
                return True
            else:
                logger.error(
                    f"Failed to update session status: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error updating session status: {str(e)}")
            manage_error(e, logger)
            return False

    def close(self):
        """Close the API session."""
        try:
            self.session.close()
            logger.info("Closed Socionator API session")
        except Exception as e:
            logger.error(f"Error closing Socionator API session: {str(e)}")
            manage_error(e, logger)