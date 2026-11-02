from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from adminsortable2.admin import (
    SortableAdminMixin,
    SortableInlineAdminMixin,
)
from tinymce.widgets import TinyMCE

from .models import (
    LearningCourse,
    LearningModule,
    Lesson,
    LessonBlock,
)


# ---------------------------------------------------------
# Настройки редактора текстовых блоков
# ---------------------------------------------------------

LESSON_EDITOR_SETUP = r"""
function(editor) {
    function getCurrentBlock(selector) {
        return editor.dom.getParent(
            editor.selection.getNode(),
            selector
        );
    }

    function openLessonCodeDialog(existingBlock = null) {
        let initialCode = '';
        let initialLanguage = 'python';
        let initialLineNumbers = true;

        if (existingBlock) {
            const codeNode = existingBlock.querySelector('code');
            const preNode = existingBlock.querySelector('pre');

            if (codeNode) {
                initialCode = codeNode.textContent || '';
            }

            if (preNode) {
                const langMatch = preNode.className.match(
                    /language-([\w-]+)/
                );

                if (langMatch) {
                    initialLanguage = langMatch[1];
                }

                initialLineNumbers = preNode.classList.contains(
                    'line-numbers'
                );
            }
        } else {
            initialCode = editor.selection.getContent({
                format: 'text'
            }).trim() || '# напишите код здесь';
        }

        editor.windowManager.open({
            title: 'Добавить / изменить блок кода',
            size: 'large',
            body: {
                type: 'panel',
                items: [
                    {
                        type: 'selectbox',
                        name: 'language',
                        label: 'Язык',
                        items: [
                            {text: 'Python', value: 'python'},
                            {text: 'HTML', value: 'markup'},
                            {text: 'CSS', value: 'css'},
                            {text: 'JavaScript', value: 'javascript'},
                            {text: 'SQL', value: 'sql'}
                        ]
                    },
                    {
                        type: 'checkbox',
                        name: 'lineNumbers',
                        label: 'Показывать номера строк'
                    },
                    {
                        type: 'textarea',
                        name: 'code',
                        label: 'Код'
                    }
                ]
            },
            initialData: {
                language: initialLanguage,
                lineNumbers: initialLineNumbers,
                code: initialCode
            },
            buttons: [
                {type: 'cancel', text: 'Отмена'},
                {
                    type: 'submit',
                    text: 'Сохранить',
                    primary: true
                }
            ],
            onSubmit: function(api) {
                const data = api.getData();
                const code = editor.dom.encode(data.code || '');
                const language = data.language || 'python';
                const lineNumbersClass = data.lineNumbers
                    ? ' line-numbers'
                    : '';

                const html =
                    '<div class="lesson-code-block">' +
                        '<pre class="language-' +
                            language + lineNumbersClass + '">' +
                            '<code class="language-' +
                                language + '">' +
                                code +
                            '</code>' +
                        '</pre>' +
                    '</div><p></p>';

                if (existingBlock) {
                    editor.dom.setOuterHTML(existingBlock, html);
                } else {
                    editor.insertContent(html);
                }

                api.close();
            }
        });
    }

    function openLessonOutputDialog(existingBlock = null) {
        let initialOutput = '';

        if (existingBlock) {
            const codeNode = existingBlock.querySelector('code');

            if (codeNode) {
                initialOutput = codeNode.textContent || '';
            }
        } else {
            initialOutput = editor.selection.getContent({
                format: 'text'
            }).trim() || 'Вывод программы';
        }

        editor.windowManager.open({
            title: 'Добавить / изменить вывод программы',
            size: 'large',
            body: {
                type: 'panel',
                items: [
                    {
                        type: 'textarea',
                        name: 'output',
                        label: 'Вывод'
                    }
                ]
            },
            initialData: {
                output: initialOutput
            },
            buttons: [
                {type: 'cancel', text: 'Отмена'},
                {
                    type: 'submit',
                    text: 'Сохранить',
                    primary: true
                }
            ],
            onSubmit: function(api) {
                const data = api.getData();
                const output = editor.dom.encode(
                    data.output || ''
                );

                const html =
                    '<div class="lesson-output-block">' +
                        '<pre><code>' +
                            output +
                        '</code></pre>' +
                    '</div><p></p>';

                if (existingBlock) {
                    editor.dom.setOuterHTML(existingBlock, html);
                } else {
                    editor.insertContent(html);
                }

                api.close();
            }
        });
    }

    editor.ui.registry.addButton('lessoncode', {
        text: 'Код',
        tooltip: 'Добавить или изменить блок кода',
        onAction: function() {
            openLessonCodeDialog(
                getCurrentBlock('div.lesson-code-block')
            );
        }
    });

    editor.ui.registry.addButton('lessonoutput', {
        text: 'Вывод',
        tooltip: 'Добавить или изменить вывод программы',
        onAction: function() {
            openLessonOutputDialog(
                getCurrentBlock('div.lesson-output-block')
            );
        }
    });

    editor.on('DblClick', function(event) {
        const codeBlock = editor.dom.getParent(
            event.target,
            'div.lesson-code-block'
        );

        if (codeBlock) {
            event.preventDefault();
            openLessonCodeDialog(codeBlock);
            return;
        }

        const outputBlock = editor.dom.getParent(
            event.target,
            'div.lesson-output-block'
        );

        if (outputBlock) {
            event.preventDefault();
            openLessonOutputDialog(outputBlock);
        }
    });

    function insertNoteBlock(blockClass, fallbackText) {
        const selectedText = editor.selection.getContent({
            format: 'text'
        }).trim();

        const content = editor.dom.encode(
            selectedText || fallbackText
        );

        editor.insertContent(
            '<div class="' + blockClass + '">' +
                content +
            '</div><p></p>'
        );
    }

    const noteButtons = [
        {
            name: 'lessondefinition',
            text: 'Термин',
            tooltip: 'Вставить блок с определением',
            blockClass: 'lesson-note-definition',
            fallback: 'Вставьте сюда важный термин или понятие.'
        },
        {
            name: 'lessonimportant',
            text: 'Важно',
            tooltip: 'Вставить блок с важной информацией',
            blockClass: 'lesson-note-important',
            fallback: 'Вставьте сюда критически важную информацию.'
        },
        {
            name: 'lessonattention',
            text: 'Внимание',
            tooltip: 'Вставить блок с замечанием',
            blockClass: 'lesson-note-attention',
            fallback: 'Вставьте сюда полезное замечание.'
        },
        {
            name: 'lessonremember',
            text: 'Запомните',
            tooltip: 'Вставить блок «Запомните»',
            blockClass: 'lesson-note-remember',
            fallback: 'Вставьте сюда то, что ученик должен запомнить.'
        }
    ];

    noteButtons.forEach(function(button) {
        editor.ui.registry.addButton(button.name, {
            text: button.text,
            tooltip: button.tooltip,
            onAction: function() {
                insertNoteBlock(
                    button.blockClass,
                    button.fallback
                );
            }
        });
    });

    editor.ui.registry.addButton('inlinecode', {
        text: 'Inline code',
        tooltip: 'Оформить код внутри строки',
        onAction: function() {
            const codeNode = getCurrentBlock(
                'code.inline-code'
            );

            if (codeNode) {
                editor.dom.remove(codeNode, true);
                return;
            }

            const selectedText = editor.selection.getContent({
                format: 'text'
            }).trim();

            const content = editor.dom.encode(
                selectedText || 'код'
            );

            editor.insertContent(
                '<code class="inline-code">' +
                    content +
                '</code>'
            );
        }
    });
}
"""


def get_lesson_editor():
    return TinyMCE(
        attrs={
            'cols': 150,
            'rows': 30,
        },
        mce_attrs={
            'width': '100%',
            'height': 700,
            'plugins': (
                'advlist autolink lists link image charmap preview anchor '
                'searchreplace visualblocks code fullscreen '
                'insertdatetime media table help wordcount '
                'hr pagebreak nonbreaking '
                'emoticons directionality paste'
            ),
            'toolbar': (
                'undo redo | formatselect styles | '
                'bold italic underline strikethrough | '
                'forecolor backcolor | '
                'alignleft aligncenter alignright alignjustify | '
                'bullist numlist outdent indent | '
                'link image media table | inlinecode | '
                'lessondefinition lessonremember '
                'lessonimportant lessonattention | '
                'lessoncode lessonoutput | '
                'code | fullscreen preview | removeformat'
            ),
            'toolbar_mode': 'wrap',
            'menubar': 'file edit view insert format tools table help',
            'paste_as_text': True,
            'content_css': 'default',
            'body_class': 'lesson-editor',
            'branding': False,
            'extended_valid_elements': (
                'div[class|style|data-language|data-line-numbers],'
                'pre[class|style],'
                'code[class|style],'
                'span[class|style]'
            ),
            'valid_children': (
                '+div[pre],+pre[code],+div[div],+div[span]'
            ),
            'setup': LESSON_EDITOR_SETUP,
        },
    )


# ---------------------------------------------------------
# Блоки урока
# ---------------------------------------------------------

class LessonBlockAdminForm(forms.ModelForm):
    content = forms.CharField(
        label='Текст',
        required=False,
        widget=get_lesson_editor(),
    )

    class Meta:
        model = LessonBlock
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get('kind')

        if kind == LessonBlock.Kind.TEXT:
            if not (cleaned_data.get('content') or '').strip():
                self.add_error(
                    'content',
                    'Добавьте текст блока.',
                )

        elif kind == LessonBlock.Kind.VIDEO:
            if not (
                cleaned_data.get('youtube_id')
                or cleaned_data.get('rutube_id')
            ):
                self.add_error(
                    'youtube_id',
                    'Укажите хотя бы один источник видео.',
                )

        elif kind == LessonBlock.Kind.PRACTICE:
            if not cleaned_data.get('practice_url'):
                self.add_error(
                    'practice_url',
                    'Укажите ссылку на практику.',
                )

        return cleaned_data


class LessonBlockInline(
    SortableInlineAdminMixin,
    admin.StackedInline,
):
    model = LessonBlock
    form = LessonBlockAdminForm
    extra = 0

    fields = (
        'kind',
        'title',
        'sort_order',
        'content',
        'youtube_id',
        'rutube_id',
        'practice_url',
    )


# ---------------------------------------------------------
# Курсы и модули
# ---------------------------------------------------------

class LessonInline(
    SortableInlineAdminMixin,
    admin.TabularInline,
):
    model = Lesson
    extra = 0
    show_change_link = True

    # Родителя и блоки редактируем на отдельной странице урока.
    # Старые поля содержания здесь больше не показываем.
    fields = ('title', 'sort_order', 'slug')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LearningModule)
class LearningModuleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'course', 'sort_order', 'slug')
    list_filter = ('course',)
    search_fields = ('title', 'slug', 'course__title')
    inlines = [LessonInline]
    prepopulated_fields = {'slug': ('title',)}


class LearningModuleInline(
    SortableInlineAdminMixin,
    admin.TabularInline,
):
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


# ---------------------------------------------------------
# Фильтры списка уроков
# ---------------------------------------------------------

class CourseListFilter(admin.SimpleListFilter):
    title = 'Курс'
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        courses = LearningCourse.objects.order_by(
            'sort_order',
            'title',
        )
        return [
            (str(course.pk), course.title)
            for course in courses
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                module__course_id=self.value(),
            )
        return queryset


class ModuleListFilter(admin.SimpleListFilter):
    title = 'Модуль'
    parameter_name = 'module_custom'

    def lookups(self, request, model_admin):
        selected_course_id = request.GET.get('course')
        modules = LearningModule.objects.select_related('course')

        if selected_course_id:
            modules = modules.filter(
                course_id=selected_course_id,
            )

        modules = modules.order_by(
            'course__sort_order',
            'course__title',
            'sort_order',
            'title',
        )

        return [
            (
                str(module.pk),
                f'{module.course.title} / {module.title}',
            )
            for module in modules
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(module_id=self.value())
        return queryset


# ---------------------------------------------------------
# Форма массового переноса уроков
# ---------------------------------------------------------

class MoveLessonsToModuleForm(forms.Form):
    _selected_action = forms.CharField(
        widget=forms.MultipleHiddenInput,
    )
    target_module = forms.ModelChoiceField(
        queryset=(
            LearningModule.objects
            .select_related('course')
            .order_by('course__title', 'sort_order', 'title')
        ),
        label='Куда перенести',
    )


# ---------------------------------------------------------
# Уроки
# ---------------------------------------------------------

@admin.register(Lesson)
class LessonAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [LessonBlockInline]

    fields = (
        'module',
        'parent',
        'title',
        'slug',
        'sort_order',
        'seo_keywords',
    )

    list_display = (
        'title',
        'module',
        'parent',
        'sort_order',
        'slug',
    )
    list_select_related = ('module__course', 'parent')
    list_filter = (CourseListFilter, ModuleListFilter)
    search_fields = (
        'title',
        'slug',
        'module__title',
        'module__course__title',
    )
    prepopulated_fields = {'slug': ('title',)}
    actions = ['move_to_module']

    def get_urls(self):
        custom_urls = [
            path(
                'move-to-module/',
                self.admin_site.admin_view(
                    self.move_to_module_view,
                ),
                name='courses_lesson_move_to_module',
            ),
        ]
        return custom_urls + super().get_urls()

    @admin.action(
        description='Перенести выбранные уроки в другой модуль',
    )
    def move_to_module(self, request, queryset):
        selected = queryset.values_list('pk', flat=True)

        return HttpResponseRedirect(
            'move-to-module/?ids='
            + ','.join(str(pk) for pk in selected)
        )

    def move_to_module_view(self, request):
        if not self.has_change_permission(request):
            raise PermissionDenied

        ids_raw = (
            request.GET.get('ids')
            or request.POST.getlist('_selected_action')
        )

        if isinstance(ids_raw, str):
            lesson_ids = [
                pk for pk in ids_raw.split(',')
                if pk.isdigit()
            ]
        else:
            lesson_ids = [
                pk for pk in ids_raw
                if str(pk).isdigit()
            ]

        queryset = (
            self.get_queryset(request)
            .filter(pk__in=lesson_ids)
            .select_related('module', 'module__course')
        )

        if request.method == 'POST':
            form = MoveLessonsToModuleForm(request.POST)

            if form.is_valid():
                target_module = form.cleaned_data['target_module']

                with transaction.atomic():
                    lessons = list(
                        queryset
                        .select_for_update()
                        .order_by('sort_order', 'title', 'pk')
                    )

                    if not lessons:
                        self.message_user(
                            request,
                            'Не выбраны уроки для переноса.',
                            level=messages.WARNING,
                        )
                        return HttpResponseRedirect('../')

                    for lesson in lessons:
                        if not self.has_change_permission(
                            request,
                            lesson,
                        ):
                            raise PermissionDenied

                    selected_ids = [
                        lesson.pk for lesson in lessons
                    ]

                    has_nested_lessons = (
                        any(
                            lesson.parent_id is not None
                            for lesson in lessons
                        )
                        or Lesson.objects.filter(
                            parent_id__in=selected_ids,
                        ).exists()
                    )

                    if has_nested_lessons:
                        self.message_user(
                            request,
                            'Перенос уроков с родителями '
                            'или подуроками пока не поддерживается.',
                            level=messages.ERROR,
                        )
                        return HttpResponseRedirect('../')

                    # Проверяем slug до сохранения всей группы.
                    slugs = [lesson.slug for lesson in lessons]

                    duplicate_selected_slugs = (
                        len(slugs) != len(set(slugs))
                    )

                    conflicts_with_target = (
                        Lesson.objects
                        .filter(
                            module=target_module,
                            slug__in=slugs,
                        )
                        .exclude(pk__in=selected_ids)
                        .exists()
                    )

                    if (
                        duplicate_selected_slugs
                        or conflicts_with_target
                    ):
                        self.message_user(
                            request,
                            'Перенос невозможен: slug уроков '
                            'должны быть уникальны внутри модуля.',
                            level=messages.ERROR,
                        )
                        return HttpResponseRedirect('../')

                    last_sort = (
                        target_module.lessons.aggregate(
                            max_sort=Max('sort_order'),
                        )['max_sort']
                        or 0
                    )

                    for lesson in lessons:
                        last_sort += 1
                        lesson.module = target_module
                        lesson.sort_order = last_sort
                        lesson.save(
                            update_fields=['module', 'sort_order'],
                        )

                self.message_user(
                    request,
                    f'Перенесено уроков: {len(lessons)}.',
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect('../')

        else:
            form = MoveLessonsToModuleForm(
                initial={
                    '_selected_action': lesson_ids,
                },
            )

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'form': form,
            'lessons': queryset,
            'title': 'Перенос уроков в другой модуль',
        }

        return render(
            request,
            'admin/courses/lesson/move_to_module.html',
            context,
        )