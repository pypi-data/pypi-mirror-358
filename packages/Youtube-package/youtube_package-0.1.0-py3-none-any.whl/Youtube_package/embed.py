from IPython.display import YouTubeVideo  # For embedding YouTube videos in Jupyter
from Youtube_package.utils import extract_video_id 

def embed_youtube(url_or_id):
    """
    Embeds a YouTube video in a Jupyter notebook.

    Args:
        url_or_id (str): YouTube URL or video ID.

    Returns:
        IPython.display.YouTubeVideo: Embedded YouTube video object.

    Raises:
        ValueError: If the provided input is not a valid YouTube URL or ID.
    """
    try:
        # Extract the video ID using the utility function
        video_id = extract_video_id(url_or_id)
        return YouTubeVideo(video_id)
    except ValueError:
        raise ValueError("Invalid YouTube URL or video ID provided.")
