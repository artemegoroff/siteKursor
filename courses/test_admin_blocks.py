from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse

from .admin import LessonBlockAdminForm
from .models import LearningCourse, LearningModule, Lesson, LessonBlock


class LessonBlockAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username='block-admin-test', is_staff=True, is_superuser=True,
        )
        cls.course = LearningCourse.objects.create(title='Blocks', slug='blocks')
        cls.module = LearningModule.objects.create(course=cls.course, title='Module', slug='module')
        cls.lesson = Lesson.objects.create(module=cls.module, title='Lesson', slug='lesson')
        cls.text = LessonBlock.objects.create(
            lesson=cls.lesson, kind='text', title='Text', sort_order=10, content='<p>Original</p>',
        )
        cls.video = LessonBlock.objects.create(
            lesson=cls.lesson, kind='video', title='Video', sort_order=20, youtube_id='video',
        )
        cls.practice = LessonBlock.objects.create(
            lesson=cls.lesson, kind='practice', title='Practice', sort_order=30,
            practice_url='https://example.com/practice',
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse('admin:courses_lesson_change', args=[self.lesson.pk])

    def block_data(self, block=None, **changes):
        data = {
            'id': block.pk if block else '',
            'lesson': self.lesson.pk,
            'kind': block.kind if block else '',
            'title': block.title if block else '',
            'sort_order': block.sort_order if block else 0,
            'content': block.content if block else '',
            'youtube_id': block.youtube_id if block else '',
            'rutube_id': block.rutube_id if block else '',
            'practice_url': block.practice_url if block else '',
        }
        data.update(changes)
        return data

    def payload(self, blocks):
        data = {
            'module': self.module.pk, 'parent': '', 'title': self.lesson.title,
            'slug': self.lesson.slug, 'seo_keywords': '', '_save': 'Save',
            'blocks-TOTAL_FORMS': len(blocks), 'blocks-INITIAL_FORMS': 3,
            'blocks-MIN_NUM_FORMS': 0, 'blocks-MAX_NUM_FORMS': 1000,
        }
        for index, block in enumerate(blocks):
            data.update({f'blocks-{index}-{name}': value for name, value in block.items()})
        return data

    def test_admin_loads_block_controls_and_assets(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/courses/lesson/blocks_inline.html')
        for asset in ['base_static/js/admin/lesson-blocks.js', 'base_static/css/admin/lesson-blocks.css']:
            self.assertContains(response, asset)
            self.assertIsNotNone(finders.find(asset))
        self.assertContains(response, 'data-block-move="up"')
        self.assertContains(response, 'data-lesson-blocks')
        self.assertContains(response, 'class="_reorder_"')

    def test_saved_and_new_blocks_accept_interleaved_order(self):
        response = self.client.post(self.url, self.payload([
            self.block_data(self.text, sort_order=3, content='<p>Edited</p>'),
            self.block_data(self.video, sort_order=1),
            self.block_data(self.practice, sort_order=4),
            self.block_data(kind='text', title='New', sort_order=2, content='<p>New text</p>'),
        ]))
        self.assertEqual(response.status_code, 302)
        blocks = list(self.lesson.blocks.all())
        self.assertEqual([block.title for block in blocks], ['Video', 'New', 'Text', 'Practice'])
        self.assertEqual([block.sort_order for block in blocks], [1, 2, 3, 4])
        self.assertEqual(blocks[2].content, '<p>Edited</p>')

    def test_blank_extra_form_does_not_create_a_block(self):
        response = self.client.post(self.url, self.payload([
            self.block_data(self.text), self.block_data(self.video),
            self.block_data(self.practice), self.block_data(),
        ]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.lesson.blocks.count(), 3)

    def test_deletion_and_reordering_can_be_saved_together(self):
        response = self.client.post(self.url, self.payload([
            self.block_data(self.text, sort_order=2),
            self.block_data(self.video, sort_order=1),
            self.block_data(self.practice, DELETE='on'),
        ]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(self.lesson.blocks.values_list('kind', flat=True)), ['video', 'text'])

    def test_hidden_values_survive_a_type_change(self):
        form = LessonBlockAdminForm(
            instance=self.text,
            data=self.block_data(self.text, kind='video', youtube_id='new-video', content='<p>Keep edited text</p>'),
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.text.refresh_from_db()
        self.assertEqual(self.text.kind, 'video')
        self.assertEqual(self.text.content, '<p>Keep edited text</p>')

    def test_inactive_unfinished_url_is_retained_without_blocking_text(self):
        form = LessonBlockAdminForm(
            instance=self.text,
            data=self.block_data(self.text, practice_url='unfinished'),
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.text.refresh_from_db()
        self.assertEqual(self.text.practice_url, 'unfinished')
        form = LessonBlockAdminForm(
            instance=self.text,
            data=self.block_data(self.text, kind='practice'),
        )
        self.assertFalse(form.is_valid())
        self.assertIn('practice_url', form.errors)

    def test_each_type_validates_its_required_content(self):
        for kind, field in [('text', 'content'), ('video', 'youtube_id'), ('practice', 'practice_url')]:
            with self.subTest(kind=kind):
                form = LessonBlockAdminForm(data=self.block_data(kind=kind))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_block_changes_require_admin_permission(self):
        self.client.logout()
        response = self.client.post(self.url, self.payload([
            self.block_data(self.text, sort_order=3), self.block_data(self.video),
            self.block_data(self.practice),
        ]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])
        self.text.refresh_from_db()
        self.assertEqual(self.text.sort_order, 10)

    def test_view_only_users_do_not_get_reorder_controls(self):
        viewer = get_user_model().objects.create(username='block-viewer', is_staff=True)
        viewer.user_permissions.add(*Permission.objects.filter(
            content_type__app_label='courses',
            codename__in=['view_lesson', 'view_lessonblock', 'view_learningmodule', 'view_learningcourse'],
        ))
        self.client.force_login(viewer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-lesson-blocks')
        self.assertNotContains(response, 'data-block-move')
        self.assertNotContains(response, 'class="module sortable"')
