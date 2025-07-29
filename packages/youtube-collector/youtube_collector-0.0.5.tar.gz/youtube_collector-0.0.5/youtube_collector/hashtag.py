import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect
from .constants import YouTubeConstants

class YouTubeHashtagCollector:
    """
    A class to collect YouTube posts by hashtag.
    """

    def __init__(self, api_key,video_type="all",
                 max_post_by_hashtag=100,
                 max_hashtag_post_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            max_post_by_hashtag (int): Maximum number of videos to collect per hashtag (default: 100)
            max_hashtag_post_retry (int): Maximum number of retries for hashtag video collection (default: 3)
        """
        self.api_key = api_key
        self.MAX_POST_BY_HASHTAG = max_post_by_hashtag
        self.MAX_HASHTAG_POST_RETRY = max_hashtag_post_retry
        self.video_type = video_type # "shorts", "all"

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_posts_by_hashtag(self, hashtag_key):
        """
        Collect videos for a single hashtag.

        Args:
            hashtag_key (str): The hashtag to collect videos for
            time_request (int, optional): Timestamp to filter videos by. If None, defaults to 6 months ago.

        Returns:
            list: A list containing the collected videos
        """
        try:

            # Get raw videos
            raw_videos = self._get_posts(hashtag_key)
            if not raw_videos:
                return []

            # Process videos
            content_full = []
            for video in raw_videos:
                try:
                    if video.get("type") == "shorts_listing":
                        continue
                    processed_video = self._process_post(video, hashtag_key)
                    if processed_video:
                        content_full.append(processed_video)
                except Exception as error:
                    print(f"Error processing video: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting videos for hashtag {hashtag_key}: {e}")
            return []

    def _get_posts(self, hashtag):
        """
        Get raw videos from API.

        Args:
            hashtag (str): The hashtag to get videos for
            time_request (int): Timestamp to filter videos by

        Returns:
            list: A list of raw videos
        """
        print("Getting videos for hashtag:", hashtag)

        url = YouTubeConstants.RAPID_URL_COLLECT_HASHTAG_VIDEOS
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        hashtag = hashtag.lower()
        params = {"tag": hashtag, "type":self.video_type}

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
                print("Load videos by hashtag error:", e)
                retry += 1


            if retry > self.MAX_HASHTAG_POST_RETRY:
                break
            if len(collected_videos) > self.MAX_POST_BY_HASHTAG:
                break

            print(f"Loop {loop_index} | Total videos {len(collected_videos)}")
            loop_index += 1

        return collected_videos

    def _process_post(self, video, hashtag_key):
        """
        Process a raw video into standardized format.

        Args:
            video (dict): Raw video data
            hashtag_key (str): The hashtag used to find this video

        Returns:
            dict: Processed video information
        """
        try:
            return {
                "search_method": "Hashtag",
                "input_kw_hst": hashtag_key,
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
                "display_url": video.get("thumbnail", [])[0].get("url"),
                "taken_at_timestamp": int(datetime.datetime.strptime(video.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").timestamp()) if video.get("publishedAt") else None,
                "music_id": None,
                "music_name": None,
                "duration": float(self._parse_duration(video.get("lengthText", "0:00"))) if video.get("lengthText") else None,
                "products": [],
                "live_events": [],
                "content_type": video.get("type"),
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
