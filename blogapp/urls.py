from django.urls import path
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    # path('', views.PostListView.as_view(), name='post_list'),
    # пример с использованием класса как контроллера
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),

    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, name='post_detail'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/comment',
         views.create_comment, name='create_comment'),
    # <slug:post> – слаг будет извлечен как строка, которая может содержать буквы, цифры, "-" и "_" (стандарт ASCII)
    # Если использование path() и конвертеров не подходит, можно задействовать
    # re_path(). Эта функция позволяет задавать шаблоны URL’ов в виде регулярных выражений.
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
]
