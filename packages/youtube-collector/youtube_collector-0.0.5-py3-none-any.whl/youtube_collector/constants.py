class YouTubeConstants:
    """
    Constants for YouTube API integration.
    """
    # API URLs
    RAPID_URL_COLLECT_CHANNEL_VIDEOS = "https://yt-api.p.rapidapi.com/channel/videos"
    RAPID_URL_COLLECT_CHANNEL_SHORT = "https://yt-api.p.rapidapi.com/channel/shorts"
    RAPID_URL_COLLECT_HASHTAG_VIDEOS = "https://yt-api.p.rapidapi.com/hashtag"
    RAPID_URL_SEARCH_VIDEOS = "https://yt-api.p.rapidapi.com/search"
    RAPID_URL_VIDEO_COMMENTS = "https://yt-api.p.rapidapi.com/comments"
    RAPID_URL_CHANNEL_ABOUT = "https://yt-api.p.rapidapi.com/channel/about"

    # API Headers
    RAPID_YT_SCRAPER_HEADER = {
        "X-RapidAPI-Host": "yt-api.p.rapidapi.com",
        "X-RapidAPI-Key": None
    }

    # Constants
    VIDEO_OVER_TIME_RANGE_LIMIT = 10  # Number of consecutive videos over time range to stop collection