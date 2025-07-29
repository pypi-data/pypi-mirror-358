# preview.py

from IPython.display import Image, HTML, display  # For rendering in Jupyter
from Youtube_package.metadata import fetch_video_metadata


def preview_youtube(url_or_id, api_key=None):
    """
    Display YouTube video thumbnail and title in a Jupyter notebook.

    Args:
        url_or_id (str): YouTube URL or video ID.
        api_key (str, optional): API key for fetch_video_metadata if needed.

    Returns:
        None. (Displays output in notebook.)
    """
    # Fetch metadata (title, author, thumbnail)
    metadata = fetch_video_metadata(url_or_id, api_key=api_key)
    title = metadata.get("title", "No Title Found")
    thumbnail_url = metadata.get("thumbnail_url")
    author = metadata.get("author", "Unknown Author")

    # Compose HTML for display: image and title with author
    html = f"""
    <div style="display:flex;align-items:center;gap:16px;">
        <img src="{thumbnail_url}" alt="Thumbnail" width="160" style="border-radius:8px;">
        <div>
            <b>{title}</b><br>
            <span style="color:gray;font-size:90%;">by {author}</span>
        </div>
    </div>
    """
    # Display the HTML in the notebook
    display(HTML(html))

# Example usage (uncomment to test in Jupyter):
# preview_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
