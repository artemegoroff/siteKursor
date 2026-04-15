from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.db.models import Max
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import LearningCourse, LearningModule, Lesson


class LessonInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('title', 'sort_order', 'slug', 'youtube_id', 'rutube_id', 'stepik')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LearningModule)
class LearningModuleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'course', 'sort_order', 'slug')
    list_filter = ('course',)
    search_fields = ('title', 'slug', 'course__title')
    inlines = [LessonInline]
    prepopulated_fields = {'slug': ('title',)}


class LearningModuleInline(SortableInlineAdminMixin, admin.TabularInline):
    model = LearningModule
    extra = 0
    fields = ('title', 'sort_order', 'slug', 'stepik')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LearningCourse)
class LearningCourseAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'slug')
    search_fields = ('title', 'slug')
    inlines = [LearningModuleInline]
    prepopulated_fields = {'slug': ('title',)}


class MoveLessonsToModuleForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    target_module = forms.ModelChoiceField(
        queryset=LearningModule.objects.select_related('course').order_by('course__title', 'sort_order', 'title'),
        label='Куда перенести',
    )


@admin.register(Lesson)
class LessonAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'module', 'sort_order', 'slug')
    list_filter = ('module', 'module__course')
    search_fields = ('title', 'slug', 'module__title', 'module__course__title')
    prepopulated_fields = {'slug': ('title',)}
    actions = ['move_to_module']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'move-to-module/',
                self.admin_site.admin_view(self.move_to_module_view),
                name='courses_lesson_move_to_module',
            ),
        ]
        return custom_urls + urls

    @admin.action(description='Перенести выбранные уроки в другой модуль')
    def move_to_module(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)
        return HttpResponseRedirect(
            f'move-to-module/?ids={",".join(str(pk) for pk in selected)}'
        )

    def move_to_module_view(self, request):
        ids_raw = request.GET.get('ids') or request.POST.getlist('_selected_action')
        if isinstance(ids_raw, str):
            lesson_ids = [pk for pk in ids_raw.split(',') if pk]
        else:
            lesson_ids = ids_raw

        queryset = Lesson.objects.filter(pk__in=lesson_ids).select_related('module', 'module__course')

        if request.method == 'POST':
            form = MoveLessonsToModuleForm(request.POST)
            if form.is_valid():
                target_module = form.cleaned_data['target_module']
                moved_count = 0

                last_sort = target_module.lessons.aggregate(max_sort=Max('sort_order'))['max_sort'] or 0

                for lesson in queryset.order_by('sort_order', 'title'):
                    last_sort += 1
                    lesson.module = target_module
                    lesson.sort_order = last_sort
                    lesson.save(update_fields=['module', 'sort_order'])
                    moved_count += 1

                self.message_user(
                    request,
                    f'Перенесено уроков: {moved_count}.',
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect('../')
        else:
            form = MoveLessonsToModuleForm(
                initial={'_selected_action': lesson_ids}
            )

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
            'lessons': queryset,
            'title': 'Перенос уроков в другой модуль',
        }
        return render(request, 'admin/courses/lesson/move_to_module.html', context)