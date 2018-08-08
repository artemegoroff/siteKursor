from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Course,ProgrammTask,InputOutputData
# Register your models here.

class AdminCourseSummernote(SummernoteModelAdmin):
    summernote_fields = ('article',)
    filter_horizontal = ['tasks']

class AdminProgrammTask(admin.ModelAdmin):
    filter_horizontal = ['examples']


admin.site.register(InputOutputData)
admin.site.register(Course,AdminCourseSummernote)
admin.site.register(ProgrammTask,AdminProgrammTask)
