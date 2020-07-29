from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Course,ProgrammTask,InputOutputData


class HaveDicision(admin.SimpleListFilter):

    title = 'have_dicision'
    parameter_name = 'decision'

    def lookups(self, request, model_admin):

        return (
            ('True', 'Нет решений'),
            ('False', 'Есть решения'),
        )

    def queryset(self, request, queryset):
        kwargs = {
            '%s' % self.parameter_name : None,
        }
        if self.value() == 'True':
            return queryset.filter(**kwargs)
        if self.value() == 'False':
            return queryset.exclude(**kwargs)
        return queryset



class AdminCourseSummernote(SummernoteModelAdmin):
    summernote_fields = ('article',)
    filter_horizontal = ['tasks']
    save_on_top = True
    list_filter = ['language']
    list_display = ['theme','number_theme','boosty','patreon','is_closed_video']
    prepopulated_fields = {"slug": ("theme",)}
    list_editable = ['number_theme','boosty','patreon','is_closed_video']



class AdminProgrammTask(admin.ModelAdmin):
    filter_horizontal = ['examples']
    list_filter = (HaveDicision,)
    search_fields = ('name',)
    list_display = ['name', 'url_ref','decision', 'boosty', 'patreon']
    list_editable = ['url_ref','decision', 'boosty', 'patreon']



admin.site.register(InputOutputData)
admin.site.register(Course,AdminCourseSummernote)
admin.site.register(ProgrammTask,AdminProgrammTask)
