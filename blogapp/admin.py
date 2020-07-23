from django.contrib import admin
from .models import Post, Comment

# модель Post добавлена на сайт администрирования
""" admin.site.register(Post) """


# Так мы говорим Django, что наша модель зарегистрирована на сайте администрирования с помощью пользовательского класса,
# наследника ModelAdmin. В нем мы указали, как отображать модель на сайте и как взаимодействовать с ней.
# Атрибут list_display позволяет перечислить поля модели, которые мы хотим отображать на странице списка.
# Декоратор @admin. register()выполняет те же действия, что и функция admin.site.register():
# регистрирует декорируемый класс – наследник ModelAdmin.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Вы можете убедиться, что теперь в списке статей отображаются те поля, которые мы указали в атрибуте list_display.
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # Справа на странице появился блок фильтрации списка, который фильтрует статьи по полям, перечисленным в list_filter
    list_filter = ('status', 'created', 'publish', 'author')
    # Также появилась строка поиска. Она добавляется для моделей, для которых определен атрибут search_fields.
    search_fields = ('tittle', 'body')
    # Мы настроили Django так, что slug генерируется автоматически из поля title с помощью атрибута prepopulated_fields.
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    # Под поиском благодаря атрибуту date_hierarchy добавлены ссылки для навигации по датам.
    date_hierarchy = 'publish'
    # По умолчанию статьи отсортированы по полям status и publish. Эта настройка задается в атрибуте ordering.
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Эта модель теперь зарегистрирована на сайте администрирования, и мы можем управлять комментариями.
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')





