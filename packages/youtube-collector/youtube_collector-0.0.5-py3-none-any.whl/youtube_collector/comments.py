import datetime
import time
import requests
from .utils import transform_selling_product, hashtag_detect
from .constants import YouTubeConstants

class YouTubeCommentCollector:
    """
    A class to collect YouTube video comments.
    """

    def __init__(self, api_key,
                 max_comment_by_post=100,
                 max_comment_retry=3):
        """
        Initialize the collector with configuration.

        Args:
            api_key (str): Your RapidAPI key
            max_comment_by_post (int): Maximum number of comments to collect per video (default: 100)
            max_comment_retry (int): Maximum number of retries for comment collection (default: 3)
        """
        self.api_key = api_key
        self.MAX_COMMENT_BY_POST = max_comment_by_post
        self.MAX_COMMENT_RETRY = max_comment_retry

        # Update headers with API key
        YouTubeConstants.RAPID_YT_SCRAPER_HEADER["X-RapidAPI-Key"] = api_key

    def collect_comments_by_post(self, video_id):
        """
        Collect comments from a YouTube video.

        Args:
            video_id (str): The video ID to collect comments from

        Returns:
            list: A list containing the collected comments
        """
        try:
            # Get raw comments
            raw_comments = self._get_comments(video_id)
            if not raw_comments:
                return []

            # Process comments
            content_full = []
            for comment in raw_comments:
                try:
                    processed_comment = self._process_comment(comment, video_id)
                    if processed_comment:
                        content_full.append(processed_comment)
                except Exception as error:
                    print(f"Error processing comment: {error}")
                    continue

            return content_full

        except Exception as e:
            print(f"Error collecting comments for video {video_id}: {e}")
            return []

    def _get_comments(self, video_id):
        """
        Get raw comments from API.

        Args:
            video_id (str): The video ID to get comments from

        Returns:
            list: A list of raw comments
        """
        print("Getting comments for video:", video_id)

        url = YouTubeConstants.RAPID_URL_VIDEO_COMMENTS
        headers = YouTubeConstants.RAPID_YT_SCRAPER_HEADER
        params = {"id": video_id}

        retry = 0
        collected_comments = []
        continuation = None

        loop_index = 0
        while True:
            if continuation is not None:
                params["continuation"] = continuation

            try:
                print("Request params:", params)
                response = requests.get(url, headers=headers, params=params)
                data = response.json()

                comments = data.get("data", [])
                continuation = data.get("continuation")

                collected_comments.extend(comments)

                if not continuation or len(comments) < 1:
                    break

            except Exception as e:
                print("Load comments error:", e)
                retry += 1

            if retry > self.MAX_COMMENT_RETRY:
                break
            if len(collected_comments) > self.MAX_COMMENT_BY_POST:
                break

            print(f"Loop {loop_index} | Total comment {len(collected_comments)}")
            loop_index += 1

        return collected_comments

    def _process_comment(self, comment, video_id):
        """
        Process a raw comment into standardized format.

        Args:
            comment (dict): Raw comment data
            video_id (str): The video ID this comment belongs to

        Returns:
            dict: Processed comment information
        """
        try:
            return {
                "comment_id": comment.get("commentId"),
                "post_id": video_id,
                "text": comment.get("textDisplay", ""),
                "num_like": self._parse_count(comment.get("likesCount", "0")),
                "num_reply": int(comment.get("replyCount", 0)),
                "user_id": comment.get("authorChannelId"),
                "user_name": comment.get("authorText"),
                "full_name": comment.get("authorText"),
                "avatar_url": comment.get("authorThumbnail", [])[0].get("url"),
                "bio": None,
                "bio_url": None,
                "num_follower": None,
                "num_following": None,
                "num_post": None,
                "youtube_channel_id": comment.get("authorChannelId"),
                "ins_id": None,
                "live_commerce": None,
                "region": None,
                "create_time": int(datetime.datetime.strptime(comment.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").timestamp()) if comment.get("publishedAt") else None,
            }
        except Exception as e:
            print(f"Error processing comment: {e}")
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
    def _parse_count(count_str):
        """
        Parse YouTube count string into integer.

        Args:
            count_str (str): Count string in format like "1.2K", "2.3M", etc.

        Returns:
            int: Parsed count
        """
        try:
            if not count_str:
                return 0
            count_str = count_str.upper()
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            return int(count_str)
        except:
            return 0 