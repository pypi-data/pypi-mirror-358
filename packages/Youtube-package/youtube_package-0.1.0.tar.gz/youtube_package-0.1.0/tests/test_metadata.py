import unittest
from Youtube_package.metadata import fetch_video_metadata

class TestFetchVideoMetadata(unittest.TestCase):
    def test_valid_url_oembed(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = fetch_video_metadata(url)
        self.assertIn("title", metadata)
        self.assertIn("author", metadata)
        self.assertIn("thumbnail_url", metadata)

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            fetch_video_metadata("https://example.com/invalid")

    def test_valid_id(self):
        video_id = "dQw4w9WgXcQ"
        metadata = fetch_video_metadata(video_id)
        self.assertIn("title", metadata)
        self.assertIn("author", metadata)
        self.assertIn("thumbnail_url", metadata)

if __name__ == "__main__":
    unittest.main()
