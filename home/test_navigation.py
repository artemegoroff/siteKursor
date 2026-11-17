from html.parser import HTMLParser

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        if tag == 'a' and href.startswith('/'):
            self.paths.append(href)


class SiteNavigationTests(SimpleTestCase):
    def test_destinations_resolve_and_courses_are_separate(self):
        request = RequestFactory().get('/')
        html = render_to_string('menuBS4.html', {'request': request})
        parser = LinkCollector()
        parser.feed(html)
        self.assertIn('/learn/basic-python/', parser.paths)
        self.assertIn('/learn/functional-python/', parser.paths)
        self.assertIn('Учебные материалы', html)
        self.assertNotIn('classynav', html)
        for path in parser.paths:
            with self.subTest(path=path):
                resolve(path)
        for asset in ['base_static/css/site-navigation.css', 'base_static/js/site-navigation.js']:
            self.assertIsNotNone(finders.find(asset))

    def test_exam_social_link_matches_section(self):
        for path, expected in [('/oge/', 'egoroff_channel_oge'), ('/ege/', 'egoroff_channel'), ('/', 'python.study')]:
            with self.subTest(path=path):
                html = render_to_string('menuBS4.html', {'request': RequestFactory().get(path)})
                self.assertIn('https://vk.com/' + expected + '"', html)
