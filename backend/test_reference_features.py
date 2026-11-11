import unittest
from unittest.mock import patch, Mock
from ai_service import normalize_recommendations, analyze_video_with_gemini, build_reference_memo
from youtube_service import validate_youtube_url, extract_frame_at, extract_youtube_description


class ReferenceFeaturesTest(unittest.TestCase):
    def test_category_ids_are_scoped_and_deduplicated(self):
        categories = {'industry': [{'id': 'i1', 'name': 'Brand'}],
                      'genre': [{'id': 'g1', 'name': 'Film'}]}
        result = normalize_recommendations(
            {'industry': ['g1', 'Brand', {'id': 'i1'}, 'made-up'],
             'genre': [{'name': ' film '}]}, categories)
        self.assertEqual(result, {'industry': ['i1'], 'genre': ['g1']})

    def test_youtube_urls_require_exact_host_and_id(self):
        for url in ['https://youtu.be/dQw4w9WgXcQ?t=5',
                    'https://www.youtube.com/watch?list=a&v=dQw4w9WgXcQ',
                    'https://www.youtube.com/shorts/dQw4w9WgXcQ']:
            self.assertTrue(validate_youtube_url(url))
        for url in ['https://evil.test/youtube.com/watch?v=dQw4w9WgXcQ',
                    'https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ',
                    'file:///youtube.com/watch?v=dQw4w9WgXcQ',
                    'https://youtube.com/watch?v=bad']:
            self.assertFalse(validate_youtube_url(url))

    @patch('ai_service.requests.post')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_ai_uses_json_and_validates_response(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {'candidates': [{'content': {'parts': [
            {'text': '{"industry":["i1"],"genre":["g1"]}'}]}}]}
        categories = {'industry': [{'id': 'i1', 'name': 'Brand'}],
                      'genre': [{'id': 'g1', 'name': 'Film'}]}
        self.assertEqual(analyze_video_with_gemini('Title', '', categories),
                         {'industry': ['i1'], 'genre': ['g1'], 'memo': ''})
        self.assertEqual(post.call_args.kwargs['json']['generationConfig']['responseMimeType'], 'application/json')

    @patch('ai_service.requests.post')
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_ai_empty_response_is_failure(self, post):
        post.return_value = Mock(ok=True, status_code=200)
        post.return_value.json.return_value = {'candidates': []}
        with self.assertRaises(ValueError):
            analyze_video_with_gemini('Title', '', {})

    def test_memo_requires_verbatim_name_and_source_evidence(self):
        result = {'entities': {
            'brands': [{'name': 'Acme', 'source': 'title', 'evidence': 'Acme campaign'}],
            'cast': [{'name': 'Kim', 'source': 'description', 'evidence': 'Starring Kim'},
                     {'name': 'Invented', 'source': 'description', 'evidence': 'Starring Invented'}],
            'locations': [{'name': 'Paris', 'source': 'thumbnail', 'evidence': 'Paris'}],
        }}
        memo = build_reference_memo(result, 'Acme campaign', 'Starring Kim')
        self.assertIn('Acme', memo)
        self.assertIn('Kim', memo)
        self.assertNotIn('Invented', memo)
        self.assertNotIn('Paris', memo)
        self.assertEqual(len(memo.splitlines()), 2)

    def test_missing_or_malformed_entities_leave_memo_empty(self):
        for entities in [None, [], {'cast': 'name'}, {'brands': [None, {'name': 123}]}]:
            self.assertEqual(build_reference_memo({'entities': entities}, '', ''), '')

    @patch('requests.get')
    def test_description_reads_only_published_player_metadata(self, get):
        get.return_value.text = 'var ytInitialPlayerResponse = {"videoDetails":{"shortDescription":"Starring Kim"}}; next();'
        self.assertEqual(extract_youtube_description('https://youtu.be/dQw4w9WgXcQ'), 'Starring Kim')

    @patch('requests.get')
    def test_description_unavailable_is_optional(self, get):
        get.return_value.text = '<html>Consent required</html>'
        self.assertEqual(extract_youtube_description('https://youtu.be/dQw4w9WgXcQ'), '')

    @patch('imageio_ffmpeg.get_ffmpeg_exe', return_value='ffmpeg')
    @patch('subprocess.run')
    @patch('youtube_service.yt_dlp.YoutubeDL')
    def test_frame_extraction_seeks_to_requested_time(self, downloader, run, ffmpeg):
        downloader.return_value.__enter__.return_value.extract_info.return_value = {
            'url': 'https://video.example/stream.mp4', 'duration': 100}
        run.return_value.stdout = b'png-data'
        result = extract_frame_at('https://youtu.be/dQw4w9WgXcQ', 42.5)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index('-ss') + 1], '42.5')
        self.assertEqual(result, b'png-data')
        self.assertEqual(run.call_args.kwargs['timeout'], 35)


if __name__ == '__main__':
    unittest.main()
