import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect
from .constants import YouTubeConstants

class YouTubeBrandCollector:
    """
    A class to collect YouTube channel information.
    """

    def __init__(self, api_key,video_type="video",
                 max_post_by_user=100,
                 max_brand_post_retry=3,
                 max_profile_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            max_post_by_user (int): Maximum number of videos to collect per channel (default: 100)
            max_brand_post_retry (int): Maximum number of retries for video collection (default: 3)
            max_profile_retry (int): Maximum number of retries for channel collection (default: 3)
        """
        self.api_key = api_key
        self.video_type = video_type  # "video", "shorts"
        self.MAX_POST_BY_USER = max_post_by_user
        self.MAX_BRAND_POST_RETRY = max_brand_post_retry
        self.MAX_PROFILE_RETRY = max_profile_retry

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_brand_posts(self, channel_id, time_request=None):
        """
        Collect videos from a YouTube channel.

        Args:
            channel_id (str): The channel's YouTube ID
            time_request (int, optional): Timestamp to filter videos by. If None, defaults to 6 months ago.

        Returns:
            list: A list containing the collected videos
        """
        try:
            if time_request is None:
                # Get current time and subtract 6 months (in seconds)
                current_time = datetime.datetime.now()
                six_months_ago = current_time - datetime.timedelta(days=180)  # Approximately 6 months
                time_request = int(six_months_ago.timestamp())

            # Get raw videos
            raw_videos = self._get_videos(channel_id, time_request)
            if not raw_videos:
                return []

            # Process videos
            content_full = []
            for video in raw_videos:
                try:
                    processed_video = self._process_video(video, channel_id)
                    if processed_video:
                        content_full.append(processed_video)
                except Exception as error:
                    print(f"Error processing video: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting channel videos for {channel_id}: {e}")
            return []

    def _get_videos(self, channel_id, time_request):
        """
        Get raw channel videos from API.

        Args:
            channel_id (str): The channel's YouTube ID
            time_request (int): Timestamp to filter videos by

        Returns:
            list: A list of raw videos
        """
        if self.video_type == "video":
            url = YouTubeConstants.RAPID_URL_COLLECT_CHANNEL_VIDEOS
        elif self.video_type == "shorts":
            url = YouTubeConstants.RAPID_URL_COLLECT_CHANNEL_SHORT
        else:
            print("Not supported type:", self.video_type)
            return []
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        params = {"id": channel_id}

        retry = 0
        collected_videos = []
        videos_check = 0
        page_token = None
        channel_meta = None

        loop_index = 0
        while True:
            if page_token is not None:
                params["token"] = page_token

            try:
                print("Request params:", params)
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                # Get channel metadata from first response
                if channel_meta is None and "meta" in data:
                    channel_meta = data["meta"]

                videos = data.get("data", [])
                page_token = data.get("continuation")

                # Add channel metadata to each video
                for video in videos:
                    video["meta"] = channel_meta

                # Check video timestamps
                for video in videos:
                    published_at = video.get("publishedAt")
                    if published_at:
                        video_time = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").timestamp()
                        if video_time < time_request:
                            videos_check += 1
                        else:
                            videos_check = 0

                collected_videos.extend(videos)

                if not page_token or len(videos) < 1:
                    break

            except Exception as e:
                print("Load channel videos error:", e)
                retry += 1

            if videos_check > YouTubeConstants.VIDEO_OVER_TIME_RANGE_LIMIT:
                break
            if retry > self.MAX_BRAND_POST_RETRY:
                break
            if len(collected_videos) > self.MAX_POST_BY_USER:
                break

            print(f"Loop {loop_index} | Total videos {len(collected_videos)}")
            loop_index += 1

        return collected_videos

    def _process_video(self, video, channel_id):
        """
        Process a raw video into standardized format.

        Args:
            video (dict): Raw video data
            channel_id (str): The channel ID used to find this video

        Returns:
            dict: Processed video information
        """
        try:
            # Get channel metadata from the video data
            meta = video.get("meta", {})
            channel_meta = {
                "channelId": meta.get("channelId"),
                "title": meta.get("title"),
                "description": meta.get("description"),
                "avatar": meta.get("avatar"),
                "metaD": meta.get("metaD"),
                "banner": meta.get("banner"),
                "channelHandle": meta.get("channelHandle"),
                "subscriberCountText": meta.get("subscriberCountText"),
                "subscriberCount": meta.get("subscriberCount"),
                "videosCountText": meta.get("videosCountText"),
                "videosCount": meta.get("videosCount")
            }

            return {
                "search_method": "Brand",
                "input_kw_hst": channel_id,
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
                "user_id": channel_id,
                "username": channel_meta.get("channelHandle", "").replace("@", ""),  # Remove @ symbol
                "bio": channel_meta.get("description"),
                "full_name": channel_meta.get("title"),
                "avatar_url": channel_meta.get("avatar",[])[0].get("url"),
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