from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # Мы создали собственный объект карты сайта, унаследовав его от Sitemap модуля sitemaps.
    # Атрибуты changefreq и priority показывают частоту обновления страниц статей и степень их совпадения
    # с тематикой сайта (максимальное значение – 1)
    changefreq = 'weekly'
    priority = 0.9

    # Метод items() возвращает QuerySet объектов, которые будут отображаться в карте сайта.
    # По умолчанию Django использует метод get_absolute_url() объектов списка, чтобы получать их URL
    # ...
    # There is no location() method in this example, but you can provide it in order to specify the URL for your object.
    # By default, location() calls get_absolute_url() on each object and returns the result.
    def items(self):
        return Post.published.all()

    # If it’s a method, it should take one argument – an object as returned by items() –
    # and return that object’s last-modified date/time as a datetime.
    def lastmod(self, obj):
        return obj.updated
