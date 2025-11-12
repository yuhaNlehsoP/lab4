from django.urls import path
from . import views

app_name = 'movie_app'

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('add/', views.add_movie, name='add_movie'),
    path('edit/<int:movie_id>/', views.edit_movie, name='edit_movie'),
    path('delete/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('upload-json/', views.upload_json, name='upload_json'),
    path('ajax-search/', views.ajax_search, name='ajax_search'),
    path('export-all/', views.export_all_movies, name='export_all_movies'),
]