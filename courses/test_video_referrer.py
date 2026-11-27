from html.parser import HTMLParser
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase


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


class LessonPlayerIntegrationTests(TestCase):
    def test_multiple_blocks_share_one_external_handler_and_have_direct_links(self):
        from .models import LearningCourse, LearningModule, Lesson, LessonBlock
        course = LearningCourse.objects.create(title='Player course', slug='player-course')
        module = LearningModule.objects.create(course=course, title='Module', slug='module')
        lesson = Lesson.objects.create(module=module, title='Lesson', slug='lesson')
        for index in range(2):
            LessonBlock.objects.create(lesson=lesson, kind='video', rutube_id=f'rutube-{index}', youtube_id=f'youtube-{index}')
        response = self.client.get(lesson.get_absolute_url())
        self.assertContains(response, 'base_static/js/lesson-video-player.js', count=1)
        self.assertContains(response, 'data-video-player', count=2)
        self.assertContains(response, 'https://www.youtube.com/watch?v=youtube-0')
        self.assertContains(response, 'https://rutube.ru/video/rutube-1/')
        self.assertNotContains(response, 'document.currentScript.previousElementSibling')
