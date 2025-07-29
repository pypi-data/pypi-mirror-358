import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect
from .constants import YouTubeConstants

class YouTubeRecentPostCollector:
    """
    A class to collect recent videos from YouTube channels.
    """

    def __init__(self, api_key, max_videos=30):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            max_videos (int): Maximum number of recent videos to collect (default: 30)
        """
        self.api_key = api_key
        self.MAX_VIDEOS = max_videos

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_posts_by_recent(self, channel_id):
        """
        Collect recent videos from a YouTube channel.

        Args:
            channel_id (str): The channel ID to collect videos from

        Returns:
            list: A list containing the collected videos
        """
        try:
            # Get raw videos
            raw_videos = self._get_videos(channel_id)
            if not raw_videos:
                return []

            # Process videos
            content_full = []
            for video in raw_videos:
                try:
                    processed_video = self._process_video(video)
                    if processed_video:
                        content_full.append(processed_video)
                except Exception as error:
                    print(f"Error processing video: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting videos for channel {channel_id}: {e}")
            return []

    def _get_videos(self, channel_id):
        """
        Get raw videos from API.

        Args:
            channel_id (str): The channel ID to get videos from

        Returns:
            list: A list of raw videos
        """
        print("Getting videos for channel:", channel_id)

        url = YouTubeConstants.RAPID_URL_COLLECT_CHANNEL_VIDEOS
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        params = {"id": channel_id}

        try:
            print("Request params:", params)
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            videos = data.get("data", [])
            return videos[:self.MAX_VIDEOS]  # Limit to max_videos

        except Exception as e:
            print("Load videos error:", e)
            return []

    def _process_video(self, video):
        """
        Process a raw video into standardized format.

        Args:
            video (dict): Raw video data

        Returns:
            dict: Processed video information
        """
        try:
            return {
                "post_id": video.get("videoId"),
                "post_link": f"www.youtube.com/watch?v={video.get('videoId')}",
                "caption": video.get("description", ""),
                "num_comment": 0,  # Not available in channel videos API
                "num_like": 0,  # Not available in channel videos API
                "num_view": (video.get("viewCount", 0)),
                "num_share": 0,
                "taken_at_timestamp": int(datetime.datetime.strptime(video.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").timestamp()),
                "display_url": video.get("thumbnail", {})[0].get("url"),
                "region": "",
                "username": video.get("channelTitle"),
                "user_id": video.get("channelId"),
                "music_id": "",
                "music_name": "",
                "duration": self._parse_duration(video.get("lengthText", "0:00")),
                "have_ecommerce_product": None,
                "ecommerce_product_count": None,
                "is_ecommerce_video": None,
                "products": None,
                "live_events": None
            }
        except Exception as e:
            print(f"Error processing video: {e}")
            return None

    @staticmethod
    def _hashtag_detect(text):
        """
        Detect hashtags in a text.

        Args:
            text (str): The text to detect hashtags in

        Returns:
            list: A list of hashtags
        """
        return hashtag_detect(text)

    @staticmethod
    def _parse_duration(duration_str):
        """
        Parse YouTube duration string into seconds.

        Args:
            duration_str (str): Duration string in format like "1:30" or "1:30:45"

        Returns:
            int: Duration in seconds
        """
        try:
            if not duration_str:
                return 0
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except:
            return 0
