from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Movie
from .forms import MovieForm, JSONUploadForm

def movie_list(request):
    # ВЫБОР ИСТОЧНИКА ДАННЫХ: БД ИЛИ ФАЙЛЫ
    source = request.GET.get('source', 'db')
    search_query = request.GET.get('query', '')
    
    if source == 'file':
        # Загрузка из JSON файла
        movies = load_movies_from_json()
        if search_query:
            movies = [m for m in movies if search_query.lower() in m['title'].lower() or 
                     search_query.lower() in m['director'].lower()]
    else:
        # Загрузка из базы данных
        if search_query:
            movies = Movie.objects.filter(
                Q(title__icontains=search_query) |
                Q(director__icontains=search_query) |
                Q(genre__icontains=search_query) |
                Q(cast__icontains=search_query)
            ).order_by('-created_at')
        else:
            movies = Movie.objects.all().order_by('-created_at')
    
    return render(request, 'movie_app/movie_list.html', {
        'movies': movies,
        'source': source,
        'search_query': search_query
    })

def add_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            save_to = form.cleaned_data['save_to']
            movie_data = {
                'title': form.cleaned_data['title'],
                'director': form.cleaned_data['director'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'duration': form.cleaned_data['duration'],
                'rating': form.cleaned_data['rating'],
                'description': form.cleaned_data['description'],
                'cast': form.cleaned_data['cast'],
                'image_url': form.cleaned_data['image_url'],
                'created_at': datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
            if save_to == 'db':
                # ПРОВЕРКА НА ДУБЛИКАТЫ В БАЗЕ ДАННЫХ
                if Movie.objects.filter(
                    title=movie_data['title'],
                    director=movie_data['director'],
                    year=movie_data['year']
                ).exists():
                    messages.error(request, '⚠ Этот фильм уже существует в базе данных!')
                    return render(request, 'movie_app/add_movie.html', {'form': form})
                
                Movie.objects.create(**movie_data)
                messages.success(request, '✅ Фильм успешно сохранен в базу данных!')
                
            elif save_to == 'json':
                save_movie_to_json(movie_data)
                messages.success(request, '✅ Фильм успешно сохранен в JSON файл!')
                
            elif save_to == 'xml':
                save_movie_to_xml(movie_data)
                messages.success(request, '✅ Фильм успешно сохранен в XML файл!')
            
            return redirect('movie_app:movie_list')
    else:
        form = MovieForm()
    
    return render(request, 'movie_app/add_movie.html', {'form': form})

def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            # ПРОВЕРКА ДУБЛИКАТОВ ПРИ РЕДАКТИРОВАНИИ
            duplicate = Movie.objects.filter(
                title=form.cleaned_data['title'],
                director=form.cleaned_data['director'],
                year=form.cleaned_data['year']
            ).exclude(id=movie_id)
            
            if duplicate.exists():
                messages.error(request, '⚠ Фильм с такими данными уже существует!')
                return render(request, 'movie_app/edit_movie.html', {'form': form, 'movie': movie})
            
            form.save()
            messages.success(request, '✅ Фильм успешно обновлен!')
            return redirect('movie_app:movie_list')
    else:
        form = MovieForm(instance=movie)
    
    return render(request, 'movie_app/edit_movie.html', {'form': form, 'movie': movie})

def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    
    if request.method == 'POST':
        movie.delete()
        messages.success(request, '✅ Фильм успешно удален!')
        return redirect('movie_app:movie_list')
    
    return render(request, 'movie_app/delete_movie.html', {'movie': movie})

def upload_json(request):
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            save_to = form.cleaned_data['save_to']
            
            try:
                data = json.load(json_file)
                added_count = 0
                duplicate_count = 0
                
                for movie_data in data:
                    if save_to == 'db':
                        # ПРОВЕРКА ДУБЛИКАТОВ ПРИ ИМПОРТЕ
                        if not Movie.objects.filter(
                            title=movie_data.get('title'),
                            director=movie_data.get('director'),
                            year=movie_data.get('year')
                        ).exists():
                            Movie.objects.create(**movie_data)
                            added_count += 1
                        else:
                            duplicate_count += 1
                    elif save_to == 'json':
                        save_movie_to_json(movie_data)
                        added_count += 1
                    elif save_to == 'xml':
                        save_movie_to_xml(movie_data)
                        added_count += 1
                
                messages.success(request, f'✅ Успешно обработано {added_count} фильмов! Дубликатов: {duplicate_count}')
                    
            except json.JSONDecodeError:
                messages.error(request, '❌ Ошибка: Неверный формат JSON файла!')
            
            return redirect('movie_app:movie_list')
    else:
        form = JSONUploadForm()
    
    return render(request, 'movie_app/upload_json.html', {'form': form})

# AJAX ПОИСК ДЛЯ ДАННЫХ ИЗ БАЗЫ
@csrf_exempt
def ajax_search(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        
        if query:
            movies = Movie.objects.filter(
                Q(title__icontains=query) |
                Q(director__icontains=query) |
                Q(genre__icontains=query) |
                Q(cast__icontains=query)
            )[:10]
            
            results = []
            for movie in movies:
                results.append({
                    'id': movie.id,
                    'title': movie.title,
                    'director': movie.director,
                    'year': movie.year,
                    'genre': movie.genre,
                    'rating': movie.rating,
                    'image_url': movie.image_url
                })
            
            return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})

def export_all_movies(request):
    movies = Movie.objects.all()
    movie_list = []
    
    for movie in movies:
        movie_list.append({
            'title': movie.title,
            'director': movie.director,
            'year': movie.year,
            'genre': movie.genre,
            'duration': movie.duration,
            'rating': movie.rating,
            'description': movie.description,
            'cast': movie.cast,
            'image_url': movie.image_url,
            'created_at': movie.created_at.strftime("%d.%m.%Y %H:%M")
        })
    
    response = HttpResponse(json.dumps(movie_list, ensure_ascii=False, indent=2), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="all_movies.json"'
    return response

# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ФАЙЛОВ
def load_movies_from_json():
    try:
        with open('movies_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_movie_to_json(movie_data):
    movies = load_movies_from_json()
    movies.append(movie_data)
    with open('movies_data.json', 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

def save_movie_to_xml(movie_data):
    try:
        tree = ET.parse('movies_data.xml')
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        root = ET.Element('movies')
        tree = ET.ElementTree(root)
    
    movie_elem = ET.SubElement(root, 'movie')
    for key, value in movie_data.items():
        child = ET.SubElement(movie_elem, key)
        child.text = str(value)
    
    tree.write('movies_data.xml', encoding='utf-8', xml_declaration=True)