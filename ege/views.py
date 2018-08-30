from django.shortcuts import render, get_object_or_404
from .models import QuestionsEGE, NumberTaskEge, VarEge, CategoryEge, VideoRazborEGE



def ege_home_page(request):
    tasksEge = NumberTaskEge.objects.all()
    varsEGE = VarEge.objects.all().order_by('number_var')
    if len(varsEGE) % 3 == 0:
        kol_elem_in_group = len(varsEGE) // 3
    else:
        kol_elem_in_group = len(varsEGE) // 3 + 1
    groups = [i * kol_elem_in_group + 1 for i in range(3)]
    context = {}
    context['tasksEge'] = tasksEge
    context['varsEGE'] = varsEGE
    context['groups'] = groups
    context['kol'] = kol_elem_in_group
    return render(request, 'ege/ege_home.html', context)


def ege_task_list(request):
    tasks = NumberTaskEge.objects.all()
    return render(request, 'task_list_all.html', {'tasks': tasks})


def ege_task_detail(request, number_task):
    exam = 'ege'
    tasks_prism = [8, 11, 14, 19, 20, 21, 24, 25]
    questions = QuestionsEGE.objects.filter(number_of_task=number_task)[::-1]
    category = list(CategoryEge.objects.filter(number_task=number_task))
    category.insert(0,'Все категории задания')
    text_cat = 'Все'
    if request.method == "POST":
        text_cat = request.POST.get("category_sel", 'Все')
        # if text_cat != 'Все':
        #     id_cat = CategoryEge.objects.get(text=text_cat)
        #     questions = QuestionsEGE.objects.filter(number_of_task=number_task).filter(category=id_cat)[::-1]
        for dataPost in request.POST:
            if not ('input' in dataPost or 'radio' in dataPost):
                continue
            num = int(dataPost[5:])

            for i in range(len(questions)):
                if questions[i].id == num:
                    if request.POST[dataPost] == "":
                        questions[i].status = 'empty'
                    elif request.POST[dataPost].lower() != questions[i].answer.lower():
                        questions[i].status = 'wrong'
                    else:
                        questions[i].status = 'good'
                    questions[i].old_answer = request.POST[dataPost]
                    break

    questions = list(questions)
    tasks = NumberTaskEge.objects.all()
    context = {"questions": questions, 'tasks': tasks,
               'number_task': NumberTaskEge.objects.all().get(number=number_task), 'exam': exam,
               'tasks_prism': tasks_prism, 'category': category, 'text_cat':text_cat}

    return render(request, 'task_detail.html', context)


def ege_get_var(request, variant_number):
    exam = 'ege_var'
    tasks_prism = ['8', '11', '14', '19', '20', '21']
    var = VarEge.objects.get(number_var=int(variant_number))
    questions = list(QuestionsEGE.objects.filter(number_of_variant=var).order_by('number_of_task'))
    if request.method == "POST":
        for dataPost in request.POST:
            if not ('input' in dataPost or 'radio' in dataPost):
                continue
            num = int(dataPost[5:])
            for i in range(len(questions)):
                if questions[i].id == num:
                    if request.POST[dataPost] != questions[i].answer:
                        questions[i].status = 'wrong'
                    else:
                        questions[i].status = 'good'
                    questions[i].old_answer = request.POST[dataPost]
                    break

    tasks = VarEge.objects.all().order_by('number_var')
    context = {"questions": questions, 'tasks': tasks, 'number_task': var, 'exam': exam,
               'tasks_prism': tasks_prism}

    return render(request, 'task_detail.html', context)


def ege_videotask_detail(request, id_task):
    razbor = get_object_or_404(VideoRazborEGE, id=int(id_task))
    task = QuestionsEGE.objects.get(q_url_video=razbor)
    context = {'vopros': task, 'video': razbor}

    return render(request, 'video_task_detail.html', context)


def ege_videotask_list(request):

    razbors = VideoRazborEGE.objects.all().order_by('-data_add')
    number_values = set(razbors.values_list('number_of_task',flat=True).distinct())
    numbers=[]
    for cat in sorted(number_values):
        numbers.append(NumberTaskEge.objects.get(number = cat))
    if len(numbers) != 1:
        numbers.insert(0,'Все видеоразборы')

    context = {'videos': razbors, 'numbers':numbers,'exam':'ege'}

    return render(request, 'video_task_list.html', context)
