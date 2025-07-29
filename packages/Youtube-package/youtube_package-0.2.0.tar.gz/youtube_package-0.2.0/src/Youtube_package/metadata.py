# metadata.py

from Youtube_package.utils import extract_video_id  # Correct module path

import requests                    # For HTTP requests

# Try importing py-youtube; handle if not installed
try:
    from pyyoutube import Api
    PYYOUTUBE_AVAILABLE = True
except ImportError:
    PYYOUTUBE_AVAILABLE = False

def fetch_video_metadata(url_or_id, api_key=None):
    """
    Fetches YouTube video metadata (title, author, thumbnail) using py-youtube or oEmbed.

    Args:
        url_or_id (str): YouTube URL or video ID.
        api_key (str, optional): YouTube Data API key for py-youtube.

    Returns:
        dict: Dictionary with keys 'title', 'author', 'thumbnail_url'.

    Raises:
        ValueError: If video metadata cannot be fetched.
    """
    # Step 1: Extract the video ID
    video_id = extract_video_id(url_or_id)
    
    # Step 2: Try to fetch metadata using py-youtube if available and api_key provided
    if PYYOUTUBE_AVAILABLE and api_key:
        try:
            api = Api(api_key=api_key)
            video_response = api.get_video_by_id(video_id=video_id)
            item = video_response.items[0].to_dict()
            return {
                "title": item["snippet"]["title"],
                "author": item["snippet"]["channelTitle"],
                "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
            }
        except Exception as e:
            # If py-youtube fails, fallback to oEmbed
            pass

    # Step 3: Fallback to YouTube's oEmbed API
    oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        resp = requests.get(oembed_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "title": data.get("title"),
                "author": data.get("author_name"),
                "thumbnail_url": data.get("thumbnail_url"),
            }
        else:
            raise ValueError("Video not found or oEmbed API error.")
    except Exception as e:
        raise ValueError(f"Could not fetch metadata: {e}")

# Example usage (uncomment to test):
# print(fetch_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
