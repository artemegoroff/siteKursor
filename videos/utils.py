
import os


# def change_number_theme(start_with, lang=Course.PYTHON, up=1):
#     themes = Course.objects.filter(number_theme__gte=start_with, language=lang).order_by(
#         '-number_theme')
#     for theme in themes:
#         theme.number_theme += up
#         theme.save()

def import_programm_task():
    file = open('data_programm_task.txt','w',encoding='utf-8')
    objs = ProgrammTask.objects.filter(decision__isnull=False)
    for i in objs:
        rez = f"{i.name};{i.decision}\n"
        file.write(rez)
    file.close()

def load_programm_task():
    file = open('data_programm_task.txt','r',encoding='utf-8')
    objs = ProgrammTask.objects.all()
    for line in file:
        name, decision = line.strip().split(';')
        elem = objs.get(name__exact=name)
        elem.decision = decision
        elem.save()
    file.close()

if __name__ == '__main__':
    print ("Starting Rango population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kursor.settings')
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    from videos.models import Course, ProgrammTask

    load_programm_task()


