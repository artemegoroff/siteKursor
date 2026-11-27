"""Per-user changelist settings without mutating the shared ModelAdmin."""
from copy import copy

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, QueryDict
from django.urls import path, reverse

from .models import Lesson, LessonListPreference, slugify

COLUMNS = (
    ('title', 'Название урока'), ('module', 'Модуль'),
    ('parent', 'Родительский урок'), ('sort_order', 'Порядок'),
    ('slug', 'Slug'), ('seo_keywords', 'SEO keywords'),
)
DEFAULT_VISIBLE = ('title', 'module', 'parent', 'sort_order', 'slug')
EDITABLE = ('title', 'slug', 'seo_keywords')


class TableSettingsForm(forms.Form):
    visible_fields = forms.MultipleChoiceField(choices=COLUMNS, required=False)
    editable_fields = forms.MultipleChoiceField(
        choices=[item for item in COLUMNS if item[0] in EDITABLE], required=False,
    )

    def clean(self):
        data = super().clean()
        visible = set(data.get('visible_fields', [])) | {'title'}
        data['visible_fields'] = [name for name, _ in COLUMNS if name in visible]
        data['editable_fields'] = [name for name in data.get('editable_fields', []) if name in visible]
        return data


class LessonListEditForm(forms.ModelForm):
    def clean(self):
        data = super().clean()
        if not self.has_changed():
            return data
        if 'slug' in self.fields and 'slug' not in data:
            return data  # The field already has a validation error.
        value = data.get('slug', self.instance.slug)
        if not value:
            value = slugify(data.get('title') or self.instance.title)
        self._effective_slug = value
        if 'slug' in self.fields:
            data['slug'] = value
        if Lesson.objects.filter(module_id=self.instance.module_id, slug=value).exclude(pk=self.instance.pk).exists():
            field = 'slug' if 'slug' in self.fields else ('title' if 'title' in self.fields else None)
            self.add_error(field, 'Такой slug уже есть у другого урока этого модуля.')
        return data


class LessonListFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        seen = set()
        for form in self.forms:
            value = getattr(form, '_effective_slug', form.instance.slug)
            if value is None:
                continue  # SQL permits multiple NULL values in this constraint.
            key = (form.instance.module_id, value)
            if key in seen:
                raise ValidationError('Уроки одного модуля должны иметь разные slug. Изменения не сохранены.')
            seen.add(key)


class LessonTablePreferencesMixin:
    list_display_links = ('title',)

    @property
    def change_list_template(self):
        return 'admin/courses/lesson/change_list.html'

    def _table_settings(self, request):
        if not hasattr(request, '_lesson_table_settings'):
            preference = LessonListPreference.objects.filter(user=request.user).first()
            raw_visible = preference.visible_fields if preference else list(DEFAULT_VISIBLE)
            raw_editable = preference.editable_fields if preference else []
            visible = set(raw_visible if isinstance(raw_visible, list) else DEFAULT_VISIBLE) & {name for name, _ in COLUMNS}
            visible.add('title')
            editable = set(raw_editable if isinstance(raw_editable, list) else []) & set(EDITABLE) & visible
            request._lesson_table_settings = (
                tuple(name for name, _ in COLUMNS if name in visible),
                tuple(name for name in EDITABLE if name in editable),
            )
        return request._lesson_table_settings

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        if request.method == 'POST' and '_save' in request.POST and not self.has_change_permission(request):
            raise PermissionDenied
        visible, editable = self._table_settings(request)
        if not self.has_change_permission(request):
            editable = ()
        local = copy(self)
        local._table_visible = visible
        local.list_display = visible
        local.list_editable = editable
        local.list_display_links = ('title',)
        if 'title' in editable:
            local.list_display = ('open_lesson',) + visible
            local.list_display_links = ('open_lesson',)
        # adminsortable2 stores this method on the instance: bind it to the copy.
        local._add_reorder_method()
        context = dict(extra_context or {})
        context['lesson_table_options'] = [
            {'name': name, 'label': label, 'visible': name in visible,
             'editable': name in editable, 'can_edit': name in EDITABLE}
            for name, label in COLUMNS
        ]
        context['lesson_table_can_edit'] = self.has_change_permission(request)
        query = request.GET.copy()
        # Ordering refers to column indexes, which change with the selected columns.
        query.pop('o', None)
        context['lesson_table_query'] = query.urlencode()
        context['lesson_table_settings_url'] = reverse('admin:courses_lesson_table_settings')
        return super(LessonTablePreferencesMixin, local).changelist_view(request, extra_context=context)

    def get_list_display(self, request):
        columns = super().get_list_display(request)
        if hasattr(self, '_table_visible') and (
            'sort_order' not in self._table_visible or not self.has_change_permission(request)
        ):
            columns = [name for name in columns if name != '_reorder_']
        return columns

    @admin.display(description='Урок')
    def open_lesson(self, obj):
        return 'Открыть'

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', LessonListEditForm)
        kwargs.setdefault('widgets', {
            'title': forms.TextInput(attrs={'size': 40}),
            'slug': forms.TextInput(attrs={'size': 24}),
            'seo_keywords': forms.Textarea(attrs={'rows': 2, 'cols': 32}),
        })
        return super().get_changelist_form(request, **kwargs)

    def get_changelist_formset(self, request, **kwargs):
        kwargs.setdefault('formset', LessonListFormSet)
        return super().get_changelist_formset(request, **kwargs)

    def get_urls(self):
        return [path('table-settings/', self.admin_site.admin_view(self.table_settings_view),
                     name='courses_lesson_table_settings')] + super().get_urls()

    def table_settings_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        if 'reset' in request.POST:
            LessonListPreference.objects.filter(user=request.user).delete()
            self.message_user(request, 'Настройки таблицы сброшены.')
        else:
            form = TableSettingsForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if not self.has_change_permission(request):
                    data['editable_fields'] = []
                LessonListPreference.objects.update_or_create(user=request.user, defaults=data)
                self.message_user(request, 'Настройки таблицы сохранены.')
            else:
                self.message_user(request, 'Настройки не сохранены: выбраны недопустимые поля.', level=messages.ERROR)
        query = QueryDict(request.POST.get('return_query', '')).copy()
        query.pop('o', None)
        target = reverse('admin:courses_lesson_changelist')
        if query:
            target += '?' + query.urlencode()
        return HttpResponseRedirect(target)
