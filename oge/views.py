from django.shortcuts import render,get_object_or_404
from .models import QuestionsOge, NumberTaskOge, VariantOge,CategoryOge,VideoRazborOGE

TASK_PRISM_JS = (6, 8, 9, 10)

def oge_home_page(request):

    context = {
        'tasks': NumberTaskOge.objects.all(),
        'vars': VariantOge.objects.all().order_by('number_var'),
        'videosOGE': len(VideoRazborOGE.objects.all()),
        'numAllTask': len(QuestionsOge.objects.all())
    }

    count_video_parse = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    videos = []
    for i in count_video_parse:
        videos.append(NumberTaskOge.objects.get(number=i))
    context['videos'] = videos

    return render(request, 'oge/oge_home.html', context)


def oge_task_detail(request, number_task):
    exam = 'oge'
    questions = QuestionsOge.objects.filter(number_of_task=number_task)
    category = list(CategoryOge.objects.filter(number_task=number_task))
    category.insert(0, 'Все категории задания')
    text_cat = 'Все'
    if request.method == "POST":
        text_cat = request.POST.get("category_sel", 'Все')
        # if text_cat != 'Все':
        #     id_cat = CategoryOge.objects.all().get(text=text_cat)
        #     questions = questions.filter(number_of_task=number_task).filter(category=id_cat)
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
    questions=list(questions)
    tasks = NumberTaskOge.objects.all()
    context = {"questions": questions,
               'tasks': tasks,
               'number_task': NumberTaskOge.objects.all().get(number=number_task),
               'exam': exam,
               'tasks_prism':TASK_PRISM_JS,
               'category':category,
               'text_cat':text_cat}

    return render(request, 'task_detail.html', context)

def oge_get_var(request,variant_number):
    exam = 'oge_var'
    var = VariantOge.objects.get(number_var=int(variant_number))
    questions = list(QuestionsOge.objects.filter(number_of_variant=var).order_by('number_of_task'))
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
    tasks = VariantOge.objects.all().order_by('number_var')
    context = {"questions": questions,
               'tasks': tasks,
               'number_task': var,
               'exam': exam,
               'tasks_prism': TASK_PRISM_JS}

    return render(request, 'task_detail.html', context)


def oge_videotask_detail(request, id_theme, id_task):
    number_values = VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct()
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))
    razbor = get_object_or_404(VideoRazborOGE, id=int(id_task))
    task = QuestionsOge.objects.get(q_url_video=razbor)
    context = {'vopros': task, 'video': razbor,'tasks': numbers,'exam':'oge'}

    return render(request, 'video_task_detail.html', context)


def oge_videotask_ONEtheme(request, id_theme):
    razbors = VideoRazborOGE.objects.filter(number_of_task=int(id_theme))
    number_values = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks': numbers, 'exam': 'oge'}

    return render(request, 'video_task_list.html', context)


def oge_videotask_AllTask(request):
    razbors = VideoRazborOGE.objects.all().order_by('-data_add')
    number_values = set(VideoRazborOGE.objects.values_list('number_of_task', flat=True).distinct())
    numbers = []
    for cat in sorted(number_values):
        numbers.append(NumberTaskOge.objects.get(number=cat))

    context = {'videos': razbors, 'tasks': numbers, 'exam': 'ege'}

    return render(request, 'video_task_list.html', context)
