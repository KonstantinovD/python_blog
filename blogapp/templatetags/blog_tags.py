from django import template
from ..models import Post
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from functools import cmp_to_key

# Для того чтобы зарегистрировать наши теги, каждый модуль с функциями тегов должен определять переменную register
register = template.Library()


# простой шаблонный тег, который возвращает количество опубликованных в блоге статей
# Django будет использовать название функции (т е total_posts) в качестве названия тега. Однако можно указать явно,
# как обращаться к тегу из шаблонов. Для этого достаточно передать в декоратор аргумент name
# @register.simple_tag(name='my_tag').
@register.simple_tag
def total_posts():
    return Post.published.count()
# Перед тем как использовать собственные шаблонные теги, необходимо подключить их в шаблоне
# с помощью {% load %}, используя имя модуля, в котором описаны теги и фильтры.


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):  # Чтобы задать другое количество статей, используйте {% show_latest_posts 3 %}
    latest_posts = Post.published.order_by("-publish")[:count]
    return {'latest_posts': latest_posts}  # функция тега возвращает словарь переменных вместо простого значения


@register.simple_tag
def get_most_commented_posts(count=3):
    posts = Post.published.all()

    def comments_cmp(x, y):  # см поле post класса Comments, теперь так можно обращаться,
        return x.comments.filter(active=True).count() - \
               y.comments.filter(active=True).count()  # хотя поля comments нет в классе Post
    max_c = list(posts)
    max_comment_posts = sorted(max_c, key=cmp_to_key(comments_cmp), reverse=True)
    return max_comment_posts[:count]
    # КОд из книги - добавляет каждому элементу новое поле 'total_comments'
    # не учитываются неактивные комменты - надо идти в таблицу comments
#   posts = Post.published.annotate(total_comments=Count('comments')) \
#              .order_by('-total_comments')[:count]
#   return posts


# Фильтр – это Python-функция, которая принимает один или два аргумента. В первый передается изменяемая переменная
# контекста, во второй – любая дополнительная переменная, второй аргумент необязателен.
# Фильтр выглядит так: {{ variable|my_filter:"foo" }}.
# Мы можем использовать последовательно сколько угодно фильтров,
# например {{ variable|filter1|filter2 }}. Каждый из них будет применяться к результату предыдущего в цепочке фильтра.
@register.filter(name='markdown')
def markdown_format(text):
    # функция mark_safe, помечает результат работы фильтра как HTML-код, который нужно учитывать при построении шаблона.
    # По умолчанию Django не доверяет любому HTML, получаемому из переменных контекста или фильтров.
    # Исключение – фрагменты, помеченные <mark_safe>. Это условие предотвращает отображение потенциально опасного HTML,
    # но в то же время позволяет обработать код, которому вы доверяете.
    # подробнее на https://docs.djangoproject.com/en/3.0/ref/utils/#django.utils.safestring.mark_safe
    return mark_safe(markdown.markdown(text))
# Создадим фильтр, чтобы добавить возможность заполнять тело статьи с помощью форматирования Markdown, которое будет
# формировать корректный HTML при отображении статьи. Markdown – синтаксис форматирования, легко используемый прямо
# в тексте, к тому же он может быть конвертирован в HTML. ( https://daringfireball.net/projects/markdown/basics )
