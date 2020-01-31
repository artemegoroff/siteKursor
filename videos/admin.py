from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Course,ProgrammTask,InputOutputData
# Register your models here.

class AdminCourseSummernote(SummernoteModelAdmin):
    summernote_fields = ('article',)
    filter_horizontal = ['tasks']
    save_on_top = True
    list_filter = ['language']
    list_display = ['theme','number_theme','language','stepic']
    prepopulated_fields = {"slug": ("theme",)}
    list_editable = ['number_theme','stepic']

class AdminProgrammTask(admin.ModelAdmin):
    filter_horizontal = ['examples']
    search_fields = ('name',)



admin.site.register(InputOutputData)
admin.site.register(Course,AdminCourseSummernote)
admin.site.register(ProgrammTask,AdminProgrammTask)
