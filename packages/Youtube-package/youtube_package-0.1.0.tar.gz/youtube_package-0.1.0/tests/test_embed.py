import unittest
from IPython.display import YouTubeVideo
from Youtube_package.embed import embed_youtube

class TestEmbedYouTube(unittest.TestCase):
    def test_embed_youtube_valid_url(self):
        # Test with a valid YouTube URL
        video = embed_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertIsInstance(video, YouTubeVideo)

    def test_embed_youtube_invalid_url(self):
        # Test with an invalid URL, expecting a ValueError
        with self.assertRaises(ValueError):
            embed_youtube("https://example.com/invalid_url")

    def test_embed_youtube_valid_id(self):
        # Test with a valid video ID
        video = embed_youtube("dQw4w9WgXcQ")
        self.assertIsInstance(video, YouTubeVideo)

if __name__ == '__main__':
    unittest.main()
