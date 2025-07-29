import datetime
import json
import time
import requests
from .constants import YouTubeConstants

class YouTubeProfileCollector:
    """
    A class to collect YouTube channel profile information.
    """

    def __init__(self, api_key):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
        """
        self.api_key = api_key

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_user_info(self, channel_id):
        """
        Collect profile information for a YouTube channel.

        Args:
            channel_id (str): The channel ID to collect profile for

        Returns:
            dict: Channel profile information
        """
        try:
            # Get raw profile data
            raw_profile = self._get_profile(channel_id)
            if not raw_profile:
                return None

            # Process profile data
            return self._process_profile(raw_profile)

        except Exception as e:
            print(f"Error collecting profile for channel {channel_id}: {e}")
            return None

    def _get_profile(self, channel_id):
        """
        Get raw profile data from API.

        Args:
            channel_id (str): The channel ID to get profile for

        Returns:
            dict: Raw profile data
        """
        print("Getting profile for channel:", channel_id)

        url = YouTubeConstants.RAPID_URL_CHANNEL_ABOUT
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        params = {"id": channel_id}

        try:
            print("Request params:", params)
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            return data

        except Exception as e:
            print("Load profile error:", e)
            return None

    def _process_profile(self, profile):
        """
        Process raw profile data into standardized format.

        Args:
            profile (dict): Raw profile data

        Returns:
            dict: Processed profile information
        """
        try:
            return {
                "user_id": profile.get("channelId", ""),
                "username": profile.get("channelHandle", "").replace("@", ""),
                "full_name": profile.get("title", ""),
                "bio": profile.get("description", ""),
                "num_follower": int(profile.get("subscriberCount", 0)),
                "num_following": 0,
                "num_post": int(profile.get("videosCount", 0)),
                "is_private": False,  
                "is_verified": None,  
                "profile_pic_url": profile.get("avatar", [])[0].get("url"),
                "external_url": [link.get("link") for link in profile.get("links", "")],
                "region": profile.get("country", "")
            }
        except Exception as e:
            print(f"Error processing profile: {e}")
            return None
