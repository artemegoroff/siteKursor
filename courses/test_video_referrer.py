from html.parser import HTMLParser
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import SimpleTestCase


class FrameParser(HTMLParser):
    frames = None

    def __init__(self):
        super().__init__()
        self.frames = []

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe':
            self.frames.append(dict(attrs))


class VideoReferrerTests(SimpleTestCase):
    def test_initial_youtube_and_switchable_players_send_origin(self):
        for rutube_id in ['', 'rutube-test']:
            with self.subTest(rutube=rutube_id):
                block = SimpleNamespace(pk=101, title='Video', youtube_id='M7lc1UVf-VE', rutube_id=rutube_id)
                html = render_to_string('courses/blocks/video.html', {'block': block})
                parser = FrameParser()
                parser.feed(html)
                self.assertEqual(len(parser.frames), 1)
                frame = parser.frames[0]
                self.assertEqual(frame['referrerpolicy'], 'strict-origin-when-cross-origin')
                expected_host = 'rutube.ru' if rutube_id else 'www.youtube.com'
                self.assertIn(expected_host, frame['src'])
                if rutube_id:
                    self.assertIn('data-video-source="youtube"', html)
                    self.assertIn('https://www.youtube.com/embed/M7lc1UVf-VE', html)
