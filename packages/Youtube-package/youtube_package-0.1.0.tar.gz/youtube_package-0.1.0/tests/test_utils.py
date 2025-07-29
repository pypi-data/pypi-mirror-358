import unittest
from Youtube_package.utils import extract_video_id

class TestExtractVideoId(unittest.TestCase):
    def test_valid_video_id(self):
        self.assertEqual(extract_video_id('dQw4w9WgXcQ'), 'dQw4w9WgXcQ')

    def test_valid_youtube_url(self):
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        self.assertEqual(extract_video_id(url), 'dQw4w9WgXcQ')

    def test_valid_short_url(self):
        url = 'https://youtu.be/dQw4w9WgXcQ'
        self.assertEqual(extract_video_id(url), 'dQw4w9WgXcQ')

    def test_invalid_url(self):
        # Testing with an invalid URL that should trigger ValueError
        with self.assertRaises(ValueError):
            extract_video_id('https://example.com/invalid_url')

    def test_invalid_length_id(self):
        # Should raise ValueError for an invalid ID format
        with self.assertRaises(ValueError):
            extract_video_id('shortid')

if __name__ == '__main__':
    unittest.main()
