import re

def extract_video_id(url_or_id):
    """
    Extracts YouTube video ID from a URL or validates raw ID.
    Raises ValueError if input is invalid.
    """
    # Check if it's already an ID (must be 11 characters, no URL)
    if isinstance(url_or_id, str) and not url_or_id.startswith("http"):
        if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
            return url_or_id
        else:
            raise ValueError("Invalid YouTube video ID format.")

    # Try extracting from known YouTube URL formats
    patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([0-9A-Za-z_-]{11})",
        r"(?:https?://)?youtu\.be/([0-9A-Za-z_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([0-9A-Za-z_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Explicitly raise ValueError if no valid ID or URL is found
    raise ValueError("Invalid YouTube URL or video ID.")
