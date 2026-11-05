import os
from pathlib import Path
import subprocess
import sys
import tempfile

from urllib.parse import urlparse
from xml.etree import ElementTree

from django.apps import apps
from django.contrib import admin
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import resolve, reverse

from .models import (
    LearningCourse, LearningModule, LegacyCourseRedirect, Lesson, LessonBlock,
)
from ege.models import NumberTaskEge, VarEge, VideoRazborEGE
from oge.models import NumberTaskOge, VariantOge, VideoRazborOGE


class CourseNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = LearningCourse.objects.create(
            title='New catalogue course', slug='new-catalogue-course', sort_order=10,
        )
        cls.module = LearningModule.objects.create(
            course=cls.course, title='Module', slug='module',
        )
        cls.parent = Lesson.objects.create(
            module=cls.module, title='Parent', slug='parent', sort_order=10,
        )
        cls.child = Lesson.objects.create(
            module=cls.module, parent=cls.parent, title='Child', slug='child',
        )
        LessonBlock.objects.create(lesson=cls.child, kind='text', content='<p>Text</p>')
        LessonBlock.objects.create(lesson=cls.child, kind='video', youtube_id='test')

    def make_redirect(self):
        return LegacyCourseRedirect.objects.create(
            old_path='python/10/', course=self.course, lesson=self.child,
        )

    def test_menu_and_home_link_to_new_catalogue(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.get_absolute_url())
        self.assertNotContains(response, '/old_course/')
        self.assertNotContains(response, 'Автоматически создано миграцией')
        courses = response.context['learning_courses']
        current = next(course for course in courses if course.pk == self.course.pk)
        self.assertEqual(current.lessons_count, 2)

    def test_home_queries_do_not_grow_with_courses_or_blocks(self):
        with CaptureQueriesContext(connection) as captured:
            self.client.get('/')
        query_count = len(captured)
        for number in range(10):
            LearningCourse.objects.create(title=f'Extra {number}', slug=f'extra-{number}')
            LessonBlock.objects.create(lesson=self.child, kind='text', content='Extra')
        with CaptureQueriesContext(connection) as captured:
            self.client.get('/')
        self.assertEqual(len(captured), query_count)
        self.assertLessEqual(query_count, 6)

    def test_empty_catalogue_renders(self):
        Lesson.objects.update(parent=None)
        LearningCourse.objects.all().delete()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Курсы скоро появятся.')
        self.assertEqual(self.client.get(reverse('courses:courses_home')).status_code, 200)

    def test_incomplete_course_is_not_linked(self):
        LearningCourse.objects.filter(pk=self.course.pk).update(slug=None)
        response = self.client.get('/')
        self.assertNotContains(response, self.course.title)

    def test_legacy_redirect_tracks_current_lesson_slug(self):
        self.make_redirect()
        for prefix in ['old_course', 'course']:
            response = self.client.get(f'/{prefix}/python/10/')
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response['Location'], self.child.get_absolute_url())
        self.child.slug = 'renamed'
        self.child.save()
        response = self.client.get('/old_course/python/10/')
        self.assertEqual(response['Location'], self.child.get_absolute_url())

    def test_deleted_lesson_falls_back_to_course(self):
        destination = self.make_redirect()
        self.child.delete()
        destination.refresh_from_db()
        self.assertIsNone(destination.lesson_id)
        response = self.client.get('/old_course/python/10/')
        self.assertEqual(response['Location'], self.course.get_absolute_url())

    def test_legacy_catalogue_redirects(self):
        for prefix in ['old_course', 'course']:
            response = self.client.get(f'/{prefix}/')
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response['Location'], reverse('courses:courses_home'))

    @override_settings(DEBUG=False)
    def test_unknown_and_retired_practice_urls_return_404(self):
        for path in ['missing/', 'decision/', 'decision/old-task/', 'test/']:
            self.assertEqual(self.client.get('/old_course/' + path).status_code, 404)

    def test_no_videos_models_admin_or_tables_remain(self):
        self.assertEqual(list(apps.get_app_config('videos').get_models()), [])
        self.assertFalse(any(model._meta.app_label == 'videos' for model in admin.site._registry))
        self.assertFalse(any(name.startswith('videos_') for name in connection.introspection.table_names()))

    def test_new_course_and_sublesson_pages_render(self):
        for item in [self.course, self.module, self.parent, self.child]:
            self.assertEqual(self.client.get(item.get_absolute_url()).status_code, 200)


class CourseSitemapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = LearningCourse.objects.create(title='Sitemap course', slug='sitemap-course')
        cls.module = LearningModule.objects.create(course=cls.course, title='Module', slug='module')
        cls.parent = Lesson.objects.create(module=cls.module, title='Parent', slug='parent')
        cls.child = Lesson.objects.create(module=cls.module, parent=cls.parent, title='Child', slug='child')
        cls.ege_task = NumberTaskEge.objects.create(number=7, title='EGE')
        cls.oge_task = NumberTaskOge.objects.create(number=10, title='OGE')
        VarEge.objects.create(number_var=4)
        VariantOge.objects.create(number_var=13)
        cls.ege_video = VideoRazborEGE.objects.create(number_of_task=cls.ege_task, url_video='test')
        cls.oge_video = VideoRazborOGE.objects.create(number_of_task=cls.oge_task, url_video='test')

    def locations(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        tree = ElementTree.fromstring(response.content)
        return [urlparse(node.text).path for node in tree.findall('{*}url/{*}loc')]

    def test_courses_modules_and_sublessons_are_listed(self):
        locations = self.locations()
        for item in [self.course, self.module, self.parent, self.child]:
            self.assertIn(item.get_absolute_url(), locations)
        self.assertFalse(any('/old_course/' in path for path in locations))

    def test_sparse_task_and_variant_numbers_are_not_fabricated(self):
        locations = self.locations()
        for path in ['/ege/task/7/', '/oge/task/10/', '/ege/var/4/', '/oge/var/13/']:
            self.assertIn(path, locations)
        self.assertNotIn('/ege/task/1/', locations)
        self.assertNotIn('/oge/var/1/', locations)

    def test_video_urls_include_both_required_arguments(self):
        locations = self.locations()
        self.assertIn(f'/ege/videotask/7/{self.ege_video.pk}/', locations)
        self.assertIn(f'/oge/videotask/10/{self.oge_video.pk}/', locations)

    def test_all_locations_resolve_and_are_unique(self):
        locations = self.locations()
        self.assertEqual(len(locations), len(set(locations)))
        for path in locations:
            self.assertIsNotNone(resolve(path))

    def test_missing_slugs_are_excluded(self):
        LearningModule.objects.filter(pk=self.module.pk).update(slug=None)
        locations = self.locations()
        self.assertNotIn(self.parent.get_absolute_url(), locations)
        self.assertNotIn(self.child.get_absolute_url(), locations)
        self.assertFalse(any('/None/' in path for path in locations))


class LegacyRetirementMigrationTests(TransactionTestCase):
    def migrate_to(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def migrate_latest(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def tearDown(self):
        self.migrate_latest()
        super().tearDown()

    def test_old_data_is_transferred_before_archived_tables_are_dropped(self):
        # 0006 is intentionally irreversible. Exercise the pre-transfer state
        # in a fresh isolated database instead of faking a production rollback.
        with tempfile.TemporaryDirectory() as directory:
            settings_file = Path(directory) / 'legacy_upgrade_settings.py'
            settings_file.write_text(
                "from Kursor.settings import *\n"
                "SECRET_KEY = 'migration-test-only'\n"
                "ALLOWED_HOSTS = ['testserver']\n"
                "SITE_ID = 1\n"
                "DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', "
                f"'NAME': {str(Path(directory) / 'upgrade.sqlite3')!r}}}}}\n"
            )
            environment = os.environ.copy()
            root = str(Path(__file__).resolve().parent.parent)
            environment['PYTHONPATH'] = os.pathsep.join([directory, root])
            environment['DJANGO_SETTINGS_MODULE'] = 'legacy_upgrade_settings'
            script = """
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client
executor = MigrationExecutor(connection)
targets = [('courses', '0001_initial'), ('videos', '0024_alter_course_youtube_id')]
executor.migrate(targets)
old_apps = executor.loader.project_state(targets).apps
OldCourse = old_apps.get_model('videos', 'Course')
Task = old_apps.get_model('videos', 'ProgrammTask')
Example = old_apps.get_model('videos', 'InputOutputData')
old = OldCourse.objects.create(
    language='PYT', slug='legacy-append', theme='Append', number_theme=7,
    article='<p>Original HTML &amp; code</p>', youtube_id='youtube',
    rutube_id='rutube', stepic='https://stepik.org/lesson/1',
)
task = Task.objects.create(name='Retired task', difficult=1)
example = Example.objects.create(input='1', output='2')
task.examples.add(example)
old.tasks.add(task)
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
from courses.models import Lesson
lesson = Lesson.objects.get(slug='legacy-append')
assert lesson.blocks.get(kind='text').content == '<p>Original HTML &amp; code</p>'
assert lesson.blocks.get(kind='video').youtube_id == 'youtube'
assert lesson.blocks.get(kind='practice').practice_url == 'https://stepik.org/lesson/1'
for path in ['python/legacy-append/', 'python/7/']:
    response = Client().get('/old_course/' + path)
    assert response.status_code == 301
    assert response['Location'] == lesson.get_absolute_url()
assert not any(name.startswith('videos_') for name in connection.introspection.table_names())
print('LEGACY_UPGRADE_OK')
"""
            result = subprocess.run(
                [sys.executable, '-c', script], cwd=root, env=environment,
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('LEGACY_UPGRADE_OK', result.stdout)

    def test_current_database_handles_moved_lessons_numeric_slugs_and_unmatched_archive(self):
        old_apps = self.migrate_to([
            ('courses', '0007_remove_legacy_lesson_content'),
            ('videos', '0024_alter_course_youtube_id'),
        ])
        OldCourse = old_apps.get_model('videos', 'Course')
        original = LearningCourse.objects.get(slug='python')
        moved = LearningCourse.objects.create(title='Moved', slug='moved-course')
        module = LearningModule.objects.create(course=moved, title='Moved module', slug='moved-module')
        numeric = Lesson.objects.create(module=module, title='Numeric slug', slug='10')
        normal = Lesson.objects.create(module=module, title='Normal', slug='normal')
        LessonBlock.objects.create(lesson=normal, kind='text', content='Edited current text')
        OldCourse.objects.create(language='PYT', slug='10', theme='Numeric', number_theme=20)
        OldCourse.objects.create(language='PYT', slug='normal', theme='Normal', number_theme=10)
        OldCourse.objects.create(language='PYT', slug='unmatched', theme='Unmatched', number_theme=30)
        self.migrate_latest()

        self.assertEqual(LegacyCourseRedirect.objects.get(old_path='python/10/').lesson_id, normal.pk)
        self.assertEqual(LegacyCourseRedirect.objects.get(old_path='python/20/').lesson_id, numeric.pk)
        self.assertEqual(LegacyCourseRedirect.objects.get(old_path='python/unmatched/').course_id, original.pk)
        self.assertEqual(normal.blocks.get().content, 'Edited current text')
