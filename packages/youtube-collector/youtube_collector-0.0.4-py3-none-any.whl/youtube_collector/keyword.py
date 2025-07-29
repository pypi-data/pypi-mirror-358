import datetime
import time
import requests

from .utils import transform_selling_product, hashtag_detect
from .constants import YouTubeConstants

class YouTubeKeywordCollector:
    """
    A class to collect YouTube videos by keyword search.
    """

    def __init__(self, api_key,video_type="video",
                 max_post_by_keyword=100,
                 max_keyword_post_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            max_post_by_keyword (int): Maximum number of videos to collect per keyword (default: 100)
            max_keyword_post_retry (int): Maximum number of retries for keyword video collection (default: 3)
        """
        self.api_key = api_key
        self.video_type = video_type # "video", "shorts"
        self.MAX_POST_BY_KEYWORD = max_post_by_keyword
        self.MAX_KEYWORD_POST_RETRY = max_keyword_post_retry

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_posts_by_keyword(self, keyword):
        """
        Collect videos for a single keyword.

        Args:
            keyword (str): The keyword to collect videos for

        Returns:
            list: A list containing the collected videos
        """
        try:
            # Get raw videos
            raw_videos = self._get_posts(keyword)
            if not raw_videos:
                return []

            # Process videos
            content_full = []
            for video in raw_videos:
                try:
                    if video.get("type") == "shorts_listing":
                        continue
                    processed_video = self._process_post(video, keyword)
                    if processed_video:
                        content_full.append(processed_video)
                except Exception as error:
                    print(f"Error processing video: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting videos for keyword {keyword}: {e}")
            return []

    def _get_posts(self, keyword):
        """
        Get raw videos from API.

        Args:
            keyword (str): The keyword to get videos for

        Returns:
            list: A list of raw videos
        """
        print("Getting videos for keyword:", keyword)

        url = YouTubeConstants.RAPID_URL_SEARCH_VIDEOS
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        params = {"query": keyword, "type":self.video_type}

        retry = 0
        collected_videos = []
        continuation = None

        loop_index = 0
        while True:
            if continuation is not None:
                params["token"] = continuation

            try:
                print("Request params:", params)
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                videos = data.get("data", [])
                continuation = data.get("continuation")

                collected_videos.extend(videos)

                if not continuation or len(videos) < 1:
                    break

            except Exception as e:
                print("Load videos by keyword error:", e)
                retry += 1

            if retry > self.MAX_KEYWORD_POST_RETRY:
                break
            if len(collected_videos) > self.MAX_POST_BY_KEYWORD:
                break

            print(f"Loop {loop_index} | Total videos {len(collected_videos)}")
            loop_index += 1

        return collected_videos

    def _process_post(self, video, keyword):
        """
        Process a raw video into standardized format.

        Args:
            video (dict): Raw video data
            keyword (str): The keyword used to find this video

        Returns:
            dict: Processed video information
        """
        try:
            return {
                "search_method": "Keyword",
                "input_kw_hst": keyword,
                "post_id": video.get("videoId"),
                "shortcode": video.get("videoId"),
                "post_link": f"www.youtube.com/watch?v={video.get('videoId')}",
                "caption": video.get("title", ""),
                "description": video.get("description", ""),
                "hashtag": ", ".join(self._hashtag_detect(video.get("description", ""))),
                "hashtags": self._hashtag_detect(video.get("description", "")),
                "created_date": video.get("publishDate"),
                "num_view": int(video.get("viewCount", 0)),
                "num_like": 0,  # Not available in basic API
                "num_comment": 0,  # Not available in basic API
                "num_share": 0,
                "num_buzz": 0,
                "num_save": 0,
                "target_country": None,
                "user_id": video.get("channelId"),
                "username": video.get("channelHandle", "").replace("@", ""),
                "bio": None,
                "full_name": video.get("channelTitle"),
                "avatar_url": None,
                "display_url": video.get("thumbnail", [])[0].get("url") if video.get("thumbnail") else None,
                "taken_at_timestamp": int(datetime.datetime.strptime(video.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").timestamp()) if video.get("publishedAt") else None,
                "music_id": None,
                "music_name": None,
                "duration": float(self._parse_duration(video.get("lengthText", "0:00"))) if video.get("lengthText") else None,
                "products": [],
                "live_events": [],
                "content_type": self.video_type,
                "brand_partnership": None,
                "user_type": None
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
            duration_str (str): Duration string in format "H:MM:SS" or "M:SS"

        Returns:
            float: Duration in seconds
        """
        try:
            parts = duration_str.split(":")
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            return 0
        except:
            return 0

    