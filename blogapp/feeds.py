from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


# Мы унаследовали наш класс от Feed – класса подсистемы фидов Django. Атрибуты title, link и description
# будут представлены в RSS элементами <title>, <link> и <description> соответственно.
class LatestPostsFeed(Feed):
    title = 'Daniil\'s personal blog'
    link = '/blog/'
    description = 'New posts of my blog.'

    # Метод items() получает объекты, которые будут включены в рассылку.
    def items(self):
        return Post.published.all()[:5]

    # Методы item_title() и item_description() получают для каждого объекта из результата items() заголовок и описание
    def item_title(self, item):
        return item.title

    # используем встроенный шаблонный фильтр truncatewords, чтобы ограничить описание статей тридцатью словами.
    def item_description(self, item):
        return truncatewords(item.body, 30)