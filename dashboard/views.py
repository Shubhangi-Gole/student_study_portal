from django.shortcuts import render
from . forms import *
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView
from .models import Notes
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")
    else:
        form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context ={'notes':notes,'form':form}
    return render(request, 'dashboard/notes.html',context)

@login_required
def delete_notes(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(DetailView):
    model = Notes
    template_name = 'dashboard/notes_detail.html'
    context_object_name = 'note'

# class NotesDetailView(generic.DetailView):
#     model = Notes
@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished = finished

            )
            homeworks.save()
            messages.success(request,f'Homework Added form {request.user.username}!!')

    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {
               'homeworks':homework,
               'homeworks_done':homework_done,
               'form':form,
               }
    return render(request, 'dashboard/homework.html',context)
@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')
@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        print(text,'To checkkkksssgfy')
        video = VideosSearch(text, limit=10)
        print(video,'video---->')
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnail': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published': i['publishedTime']

            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
            context={
                'form': form,
                'results' : result_list
            }
        return render(request, 'dashboard/youtube.html', context)

    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request,"dashboard/youtube.html", context)


# def youtube(request):
#     result_list = []
#     form = DashboardForm(request.POST or None)
#
#     if request.method == 'POST' and form.is_valid():
#         text = form.cleaned_data['text']
#         video = VideosSearch(text, limit=10)
#         for i in video.result()['result']:
#             desc = ''
#             if i.get('descriptionSnippet'):
#                 desc = ''.join([j['text'] for j in i['descriptionSnippet']])
#             result_list.append({
#                 'input': text,
#                 'title': i['title'],
#                 'duration': i['duration'],
#                 'thumbnail': i['thumbnails'][0]['url'],
#                 'channel': i['channel']['name'],
#                 'link': i['link'],
#                 'views': i['viewCount']['short'],
#                 'published': i['publishedTime'],
#                 'description': desc
#             })
#
#     return render(request, 'dashboard/youtube.html', {'form': form, 'results': result_list})
#
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user= request.user,
                title= request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo Added form {request.user.username}!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form': form,
        'todos': todo,
        'todos_done': todos_done
    }
    return render(request, "dashboard/todo.html",context)
@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')
@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")

def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')

            }

            result_list.append(result_dict)
            context={
                'form': form,
                'results' : result_list
            }
        return render(request, 'dashboard/books.html', context)

    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request,"dashboard/books.html", context)


# def books(request):
#     form = DashboardForm()
#     context = {'form':form}
#     return render(request,"dashboard/books.html",context)

# def dictionary(request):
#     if request.method == 'POST':
#         form = DashboardForm(request.POST)
#         text = request.POST['text']
#         url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"
#         r = requests.get(url)
#         answer = r.json()
#         try:
#             phonetics = answer[0]['phonetics'][0]['text']
#             audio = answer[0]['phonetics'][0]['audio']
#             definition = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('definition', '')
#             example = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('example', '')
#             synonyms = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0].get('synonyms', [])
#             audio = answer[0].get('phonetics', [{}])[0].get('audio', '')
#
#             # definition = answer[0].get['meanings'][0].get['definition'][0].get['definition']
#             # example = answer[0].get['meanings'][0].get['definitions'][0].get['example']
#             # synonyms = answer[0].get['meanings'][0].get['definitions'][0].get['synonyms']
#             context = {
#                 'form': form,
#                 'input': text,
#                 'phonetics': phonetics,
#                 'audio': audio,
#                 'definition': definition,
#                 'example': example,
#                 'synonyms': synonyms
#             }
#         except:
#             context = {
#                 'form': form,
#                 'input': text
#             }
#         return render(request, "dashboard/dictionary.html", context)
#     else:
#         form = DashboardForm()
#         context = {'form': form}
#     return render(request, "dashboard/dictionary.html", context)
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '').strip()
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{text}"

        try:
            r = requests.get(url)
            r.raise_for_status()
            answer = r.json()

            # Get first phonetic text and first audio
            phonetics_list = answer[0].get('phonetics', [])
            phonetics = ''
            audio = ''
            for p in phonetics_list:
                if not phonetics and p.get('text'):
                    phonetics = p['text']
                if not audio and p.get('audio'):
                    audio = p['audio']
                if phonetics and audio:
                    break

            # Get first definition and example
            meanings = answer[0].get('meanings', [])
            definition = ''
            example = ''
            synonyms = []

            for meaning in meanings:
                defs = meaning.get('definitions', [])
                for d in defs:
                    if not definition and d.get('definition'):
                        definition = d['definition']
                    if not example and d.get('example'):
                        example = d['example']
                    if d.get('synonyms'):
                        synonyms.extend(d['synonyms'])
                    if definition and example:
                        break
                if definition and example:
                    break

            # Also check top-level synonyms
            for meaning in meanings:
                if meaning.get('synonyms'):
                    synonyms.extend(meaning['synonyms'])

            # Remove duplicates
            synonyms = list(set(synonyms))

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }

        except Exception:
            context = {
                'form': form,
                'input': text,
                'error': 'No definition found or API error.'
            }

        return render(request, "dashboard/dictionary.html", context)

    else:
        form = DashboardForm()
        return render(request, "dashboard/dictionary.html", {'form': form})

def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form': form,
            'title': search.title,
            'link': search.url,
            'details': search.summary
        }
        return render(request, "dashboard/wiki.html", context)
    else:
        form = DashboardForm()
        context = {
            'form': form
        }
    return render(request, "dashboard/wiki.html", context)
#
# def conversion(request):
#     if request.method == "POST":
#         form = ConversionForm(request.POST)
#         if request.POST['measurement'] == 'length':
#             measurement_form = ConversionLengthForm()
#             context = {
#                 'form': form,
#                 'm_form': measurement_form,
#                 'input': True
#
#             }
#             if 'input' in request.POST:
#                 first = request.POST['measure1']
#                 second = request.POST['measure2']
#                 input = request.POST['input']
#                 answer = ''
#                 if input and int(input)>=0:
#                     if first == 'yard' and second == 'foot':
#                         answer = f'{input} yard = {int(input)*3} foot'
#                     if first == 'foot' and second == 'yard':
#                         answer = f'{input} foot = {int(input)/3} yard'
#                 context = {
#                     'form': form,
#                     'm_form': measurement_form,
#                     'input': True,
#                     'answer': answer
#                 }
#
#
#             if request.POST['measurement'] == 'mass':
#                 measurement_form = ConversionMassForm()
#                 context = {
#                     'form': form,
#                     'm_form': measurement_form,
#                     'input': True
#
#                 }
#                 if 'input' in request.POST:
#                     first = request.POST['measure1']
#                     second = request.POST['measure2']
#                     input = request.POST['input']
#                     answer = ''
#                     if input and int(input) >= 0:
#                         if first == 'pound' and second == 'kilogram':
#                             answer = f'{input} pound = {int(input) *0.453592} kilogram'
#                         if first == 'kilogram' and second == 'pound':
#                             answer = f'{input} kilogram = {int(input)*2.20462} pound'
#                     context = {
#                         'form': form,
#                         'm_form': measurement_form,
#                         'input': True,
#                         'answer': answer
#                     }
#         else:
#             form = ConversionForm()
#             context = {
#                 'form': form,
#                 'input': False
#             }
#
#         return render(request, "dashboard/conversion.html", context)

def conversion(request):
    form = ConversionForm(request.POST or None)
    action = request.POST.get('action')
    measurement_type = request.POST.get('measurement')
    context = {
        'form': form,
        'input': False
    }

    if request.method == "POST":
        if action == 'select':
            if measurement_type == 'length':
                measurement_form = ConversionLengthForm()
            elif measurement_type == 'mass':
                measurement_form = ConversionMassForm()
            else:
                measurement_form = None

            context.update({
                'm_form': measurement_form,
                'input': True
            })

        elif action == 'convert':
            input_value = request.POST.get('input')
            first = request.POST.get('measure1')
            second = request.POST.get('measure2')
            answer = ''
            measurement_form = None

            try:
                value = float(input_value)
                if measurement_type == 'length':
                    measurement_form = ConversionLengthForm(request.POST)
                    if first == 'yard' and second == 'foot':
                        answer = f'{value} yard = {value * 3:.2f} foot'
                    elif first == 'foot' and second == 'yard':
                        answer = f'{value} foot = {value / 3:.2f} yard'
                elif measurement_type == 'mass':
                    measurement_form = ConversionMassForm(request.POST)
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{value} pound = {value * 0.453592:.2f} kilogram'
                    elif first == 'kilogram' and second == 'pound':
                        answer = f'{value} kilogram = {value * 2.20462:.2f} pound'
            except (ValueError, TypeError):
                answer = "Invalid input. Please enter a valid number."

            context.update({
                'm_form': measurement_form,
                'input': True,
                'answer': answer
            })

        # ✅ Add a fallback return for unexpected POST actions
        return render(request, "dashboard/conversion.html", context)

    # ✅ Always return for GET requests
    return render(request, "dashboard/conversion.html", context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}!!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {
        'form': form
    }
    return render(request,"dashboard/register.html", context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks' : homeworks,
        'todos' : todos,
        'homework_done' : homework_done,
        'todos_done' : todos_done
    }
    return render(request, "dashboard/profile.html",context)