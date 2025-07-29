# YouTube Collector

A Python library for collecting YouTube data including channel videos, hashtag videos, keyword search, comments, and channel profiles.

## Features

- Collect posts by hashtag
- Collect tagged posts for a user
- Collect posts from brand accounts
- Collect comments from posts
- Support for multiple API providers (RocketAPI and SocialAPI4)
- Rate limiting and error handling
- Pagination support
- Time-based filtering

## Installation

```bash
pip install youtube-collector
```

## Usage

### Collecting Channel Videos

```python
from youtube_collector import YouTubeBrandCollector

collector = YouTubeBrandCollector(api_key="your_api_key")
videos = collector.collect_brand_posts(channel_id="your_channel_id")
print(videos)
```

### Collecting Hashtag Videos

```python
from youtube_collector import YouTubeHashtagCollector

collector = YouTubeHashtagCollector(api_key="your_api_key")
videos = collector.collect_posts_by_hashtag(hashtag_key="your_hashtag")
print(videos)
```

### Collecting Keyword Videos

```python
from youtube_collector import YouTubeKeywordCollector

collector = YouTubeKeywordCollector(api_key="your_api_key")
videos = collector.collect_posts_by_keyword(keyword="your_keyword")
print(videos)
```

### Collecting Comments

```python
from youtube_collector import YouTubeCommentCollector

collector = YouTubeCommentCollector(api_key="your_api_key")
comments = collector.collect_comments(video_id="your_video_id")
print(comments)
```

### Collecting Channel Profile

```python
from youtube_collector import YouTubeProfileCollector

collector = YouTubeProfileCollector(api_key="your_api_key")
profile = collector.collect_profile(channel_id="your_channel_id")
print(profile)
```

### Collecting Recent Videos

```python
from youtube_collector import YouTubeRecentPostCollector

collector = YouTubeRecentPostCollector(api_key="your_api_key")
videos = collector.collect_recent_posts(channel_id="your_channel_id")
print(videos)
```

## Configuration

The library supports various configuration options:

- `max_hashtag_post_retry`: Maximum retries for hashtag posts (default: 3)
- `max_tagged_post_retry`: Maximum retries for tagged posts (default: 3)
- `max_brand_post_retry`: Maximum retries for brand posts (default: 3)
- `max_comment_retry`: Maximum retries for comments (default: 3)

## Error Handling

The library includes built-in error handling and retry mechanisms:

- Automatic retry on API failures
- Rate limiting to prevent API throttling
- Time-based filtering to limit data collection
- Exception handling for malformed responses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 