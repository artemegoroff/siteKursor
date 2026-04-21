from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.db.models import Max
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from tinymce.widgets import TinyMCE

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


class CourseListFilter(admin.SimpleListFilter):
    title = 'Курс'
    parameter_name = 'course'

    def lookups(self, request, model_admin):
        courses = LearningCourse.objects.order_by('sort_order', 'title')
        return [(str(course.id), course.title) for course in courses]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(module__course_id=self.value())
        return queryset


class ModuleListFilter(admin.SimpleListFilter):
    title = 'Модуль'
    parameter_name = 'module_custom'

    def lookups(self, request, model_admin):
        selected_course_id = request.GET.get('course')

        modules = LearningModule.objects.select_related('course')

        if selected_course_id:
            modules = modules.filter(course_id=selected_course_id)

        modules = modules.order_by('course__sort_order', 'course__title', 'sort_order', 'title')

        return [
            (str(module.id), f'{module.course.title} / {module.title}')
            for module in modules
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(module_id=self.value())
        return queryset


class LessonAdminForm(forms.ModelForm):
    article = forms.CharField(
        required=False,
        widget=TinyMCE(
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
                    'link image media table | '
                    'lessondefinition lessonimportant lessonattention | '
                    'lessoncode lessonoutput | '
                    'code | '
                    'fullscreen preview | '
                    'removeformat'
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
                'valid_children': '+div[pre],+pre[code],+div[div],+div[span]',
                'setup': '''
    function(editor) {
        function getCurrentCodeBlock() {
            const node = editor.selection.getNode();
            return editor.dom.getParent(node, 'div.lesson-code-block');
        }

        function getCurrentOutputBlock() {
            const node = editor.selection.getNode();
            return editor.dom.getParent(node, 'div.lesson-output-block');
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
                    const className = preNode.className || '';
                    const langMatch = className.match(/language-([\\w-]+)/);
                    if (langMatch) {
                        initialLanguage = langMatch[1];
                    }

                    initialLineNumbers = className.indexOf('line-numbers') !== -1;
                }
            } else {
                const selectedText = editor.selection.getContent({ format: 'text' }).trim();
                initialCode = selectedText || '# напишите код здесь';
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
                                { text: 'Python', value: 'python' },
                                { text: 'HTML', value: 'markup' },
                                { text: 'CSS', value: 'css' },
                                { text: 'JavaScript', value: 'javascript' },
                                { text: 'SQL', value: 'sql' }
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
                    { type: 'cancel', text: 'Отмена' },
                    { type: 'submit', text: 'Сохранить', primary: true }
                ],
                onSubmit: function(api) {
                    const data = api.getData();
                    const code = editor.dom.encode(data.code || '');
                    const language = data.language || 'python';
                    const lineNumbersClass = data.lineNumbers ? ' line-numbers' : '';

                    const html =
                        '<div class="lesson-code-block">' +
                            '<pre class="language-' + language + lineNumbersClass + '">' +
                                '<code class="language-' + language + '">' + code + '</code>' +
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
                const selectedText = editor.selection.getContent({ format: 'text' }).trim();
                initialOutput = selectedText || 'Вывод программы';
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
                    { type: 'cancel', text: 'Отмена' },
                    { type: 'submit', text: 'Сохранить', primary: true }
                ],
                onSubmit: function(api) {
                    const data = api.getData();
                    const output = editor.dom.encode(data.output || '');

                    const html =
                        '<div class="lesson-output-block">' +
                            '<pre><code>' + output + '</code></pre>' +
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
                const block = getCurrentCodeBlock();
                openLessonCodeDialog(block);
            }
        });

        editor.ui.registry.addButton('lessonoutput', {
            text: 'Вывод',
            tooltip: 'Добавить или изменить блок вывода программы',
            onAction: function() {
                const block = getCurrentOutputBlock();
                openLessonOutputDialog(block);
            }
        });

        editor.on('DblClick', function(e) {
            const codeBlock = editor.dom.getParent(e.target, 'div.lesson-code-block');
            if (codeBlock) {
                e.preventDefault();
                openLessonCodeDialog(codeBlock);
                return;
            }

            const outputBlock = editor.dom.getParent(e.target, 'div.lesson-output-block');
            if (outputBlock) {
                e.preventDefault();
                openLessonOutputDialog(outputBlock);
            }
        });
        
        function insertNoteBlock(blockClass, fallbackText) {
            const selectedText = editor.selection.getContent({ format: 'text' }).trim();
            const content = selectedText || fallbackText;
            const encoded = editor.dom.encode(content);
        
            editor.insertContent(
                '<div class="' + blockClass + '">' +
                    encoded +
                '</div>' +
                '<p></p>'
            );
        }
        
        editor.ui.registry.addButton('lessondefinition', {
            text: 'Термин',
            tooltip: 'Вставить блок с определением',
            onAction: function() {
                insertNoteBlock(
                    'lesson-note-definition',
                    'Вставьте сюда важный термин или понятие.'
                );
            }
        });
        
        editor.ui.registry.addButton('lessonimportant', {
            text: 'Важно',
            tooltip: 'Вставить блок с важной информацией',
            onAction: function() {
                insertNoteBlock(
                    'lesson-note-important',
                    'Вставьте сюда критически важную информацию.'
                );
            }
        });
        
        editor.ui.registry.addButton('lessonattention', {
            text: 'Внимание',
            tooltip: 'Вставить блок с замечанием',
            onAction: function() {
                insertNoteBlock(
                    'lesson-note-attention',
                    'Вставьте сюда полезное замечание.'
                );
            }
        });
    }
''',
            }
        ),
        label='Текст урока',
    )

    class Meta:
        model = Lesson
        fields = '__all__'


@admin.register(Lesson)
class LessonAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = LessonAdminForm  # 👈 ВАЖНО
    list_display = ('title', 'module', 'sort_order', 'slug')
    list_filter = (CourseListFilter, ModuleListFilter)
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
