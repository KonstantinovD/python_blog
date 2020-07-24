from django.contrib.sessions import serializers
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from django.contrib import messages
from taggit.models import Tag
from django.db.models import Count  # функция агрегации Count из Django (еще есть Min, Max, Avg).
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)  # По 3 статьи на каждой странице.
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
    return render(request,'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    # Список активных комментариев для этой статьи.
    comments = post.comments.filter(active=True)
    comment_form = CommentForm()
    page_dict = {'post': post, 'comments': comments, 'comment_form': comment_form,
                 'new_comment': request.session.get('new_comment', None)}

    # Формирование списка похожих статей.
    # получает все ID тегов текущей статьи. Метод QuerySet’а values_list() возвращает кортежи со значениями
    # заданного поля. Мы указали flat=True, чтобы получить «плоский» список вида [1, 2, 3, ...];
    post_tags_ids = post.tags.values_list('id', flat=True)
    # ...
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    # использует функцию агрегации Count для формирования вычисляемого поля same_tags,
    # которое содержит определенное количество совпадающих тегов;
    # сортирует список опубликованных статей в убывающем порядке по количеству совпадающих тегов для отображения
    # первыми максимально похожих статей и делает срез результата для отображения только четырех статей.
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]
    page_dict['similar_posts'] = similar_posts

    return render(request, 'blog/post/detail.html', page_dict)


# Если заменить <post> на <slug>, например, то получите
# create_comment() got an unexpected keyword argument 'post'
def create_comment(request, year, month, day, post):
    new_post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    comment_form = CommentForm()
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил комментарий.
        # request.method = 'GET'
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохраняем в базе данных.
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье.
            new_comment.post = new_post
            # И только потом сохраняем комментарий в базе данных.
            new_comment.save()
            # details_dict = {'new_comment': new_comment, 'comment_form': comment_form}
            # request.session['new_comment'] = True
            # request.session.modified = True
            messages.add_message(request, messages.SUCCESS, "Your comment has been added")
            # messages.add_message(request, messages.SUCCESS, "HAHAHA") - spoiled
    return HttpResponseRedirect(request.path.replace('/comment', ''))
    # return redirect(request, 'blog/post/detail.html', new_comment=new_comment, comment_form=comment_form)
    # post_detail(request, year, month, day, post, new_comment=new_comment, comment_form=comment_form)


# Аналог функции post_list
class PostListView(ListView):
    queryset = Post.published.all()

    # использовать posts в качестве переменной контекста HTML-шаблона, в которой будет храниться список объектов.
    # Если не указать атрибут context_object_name, по умолчанию используется переменная object_list;
    context_object_name = 'posts'

    # Для поддержки постраничного вывода мы должны передавать объект страницы, содержащий список статей, в HTML-шаблон.
    # Базовый обработчик Django ListView передает этот объект в качестве переменной с именем page_obj, поэтому нужно
    # немного откорректировать post/list.html и, подключая шаблон постраничного вывода, указать эту переменную:
    # {% include "pagination.html" with page=page_obj %}
    paginate_by = 3

    # использовать указанный шаблон для формирования страницы. Если бы мы не указали template_name,
    # то базовый класс ListView использовал бы шаблон blog/post_list.html.
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    form = EmailPostForm()
    sent = False
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            cd = form.cleaned_data

            # Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'\
                .format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'\
                .format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            sent = True
    #     else:
    #         # Если форма не проходит валидацию, то в атрибут <cleaned_data> попадут только корректные поля.
    #         form = EmailPostForm()
    #         return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
    # else:
    #     form = EmailPostForm()
    #     return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    # Поисковый запрос отправляется методом GET, чтобы результирующий URL содержал в себе фразу поиска в параметре query
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_query = SearchQuery(query)

            if form.cleaned_data['header']:
                # Мы можем повысить значимость некоторых векторов, чтобы совпадения по ним считались более релевантными,
                # чем по остальным. Например, можно настроить поиск так, чтобы статьи с совпадениями в заголовке были
                # в большем приоритете перед статьями с совпадениями в содержимом.
                # Применяем векторы по полям title и body с разным весом. По умолчанию используются веса D, C, B и A,
                # которые соответствуют числам 0.1, 0.2, 0.4 и 1. Мы применили вес 1.0 для вектора по полю title
                # и 0.4 – для вектора по полю body. В конце показываем только те статьи, чей ранг выше 0.3.
                search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
                results = Post.objects.annotate(
                    rank=SearchRank(search_vector, search_query)
                ).filter(rank__gte=0.3).order_by('-rank')
            else:
                search_vector = SearchVector('title', 'body')
                # В этом фрагменте мы создаем объект SearchQuery, фильтруем с его помощью
                # результаты и используем SearchRank для ранжирования статей.
                results = Post.objects.annotate(
                    search=search_vector,
                    rank=SearchRank(search_vector, search_query)
                ).filter(search=query).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
    # Еще одна возможность поиска – по сходству триграмм. Триграмма – это последовательность из трех символов.
    # Вы можете измерить подобие двух строк, подсчитав количество совпадений триграмм. Такая метрика на практике
    # является очень эффективной для определения подобия строк или слов во многих языках.
    # Чтобы использовать триграммы в PostgerSQL, необходимо в postgres подключить расширение pg_trgm
