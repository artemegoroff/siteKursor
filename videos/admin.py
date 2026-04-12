from django import forms
from django.contrib import admin
from tinymce.widgets import TinyMCE

from .models import Course, ProgrammTask, InputOutputData


class HaveDecision(admin.SimpleListFilter):
    title = 'have_dicision'
    parameter_name = 'decision'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Нет решений'),
            ('False', 'Есть решения'),
        )

    def queryset(self, request, queryset):
        kwargs = {
            self.parameter_name: None,
        }
        if self.value() == 'True':
            return queryset.filter(**kwargs)
        if self.value() == 'False':
            return queryset.exclude(**kwargs)
        return queryset


class CourseAdminForm(forms.ModelForm):
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
                # 'menubar': True,

                'plugins': (
                    'advlist autolink lists link image charmap preview anchor '
                    'searchreplace visualblocks code fullscreen '
                    'insertdatetime media table help wordcount '
                    'codesample hr pagebreak nonbreaking '
                    'emoticons directionality paste'
                ),

                'toolbar': (
                    'undo redo | formatselect styles | '
                    'bold italic underline strikethrough | '
                    'forecolor backcolor | '
                    'alignleft aligncenter alignright alignjustify | '
                    'bullist numlist outdent indent | '
                    'link image media table | '
                    'codesample code | '
                    'fullscreen preview | '
                    'removeformat'
                ),

                'toolbar_mode': 'wrap',  # перенос строк, чтобы не обрезалось

                'menubar': 'file edit view insert format tools table help',
                'paste_as_text': True,  # чтобы не тащился мусор из Word
                'content_css': 'default',
                'body_class': 'lesson-editor',
                'branding': False,
            }
        ),
        label='article',
    )

    class Meta:
        model = Course
        fields = '__all__'


@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    form = CourseAdminForm
    filter_horizontal = ['tasks']
    save_on_top = True
    list_filter = ['language']
    list_display = ['theme', 'number_theme', 'youtube_id', 'rutube_id', 'is_closed_video']
    prepopulated_fields = {"slug": ("theme",)}
    list_editable = ['number_theme', 'youtube_id', 'rutube_id', 'is_closed_video']


@admin.register(ProgrammTask)
class AdminProgramTask(admin.ModelAdmin):
    filter_horizontal = ['examples']
    list_filter = (HaveDecision,)
    search_fields = ('name',)
    list_display = ['name', 'url_ref', 'decision', 'boosty', 'patreon']
    list_editable = ['url_ref', 'decision', 'boosty', 'patreon']


@admin.register(InputOutputData)
class InputOutputDataAdmin(admin.ModelAdmin):
    pass
