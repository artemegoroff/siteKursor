import json
import re

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, RequestFactory
from django.http import Http404
from courses.landing_views import detail
from django.urls import reverse

from Kursor.sitemaps import CourseLandingSiteMap


class LandingTests(SimpleTestCase):
    def test_landing_and_canonical_metadata(self):
        response = self.client.get('/learn/python/?utm_source=test')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(schema['@type'], 'Course')
        self.assertTrue(schema['isAccessibleForFree'])
        self.assertEqual(schema['url'], 'http://testserver/learn/python/')
        self.assertContains(response, 'https://stepik.org/course/63085/promo')
        self.assertContains(response, 'data-demo-form')

    def test_unknown_course(self):
        with self.assertRaises(Http404):
            detail(RequestFactory().get('/learn/missing/'), 'missing')

    def test_sitemap_and_assets(self):
        sitemap = CourseLandingSiteMap()
        self.assertEqual(sitemap.items(), ['python'])
        self.assertEqual(sitemap.location('python'), reverse('course_landings:detail', kwargs={'course_slug': 'python'}))
        for asset in ['base_static/css/landing/python.css', 'base_static/js/landing/python.js']:
            self.assertIsNotNone(finders.find(asset))
