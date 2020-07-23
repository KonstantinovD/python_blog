from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    # это поле заголовка статьи. Оно определено как тип CharField, который соответствует типу VARCHAR в базе данных;
    title = models.CharField(max_length=250)

    # это поле будет использоваться для формирования URL’ов. Слаг – короткое название, содержащее только буквы, цифры и
    # символы "-" и "_". Мы будем использовать slug для построения семантических URL’ов (friendly URLs) для статей
    # Мы также добавили параметр  <unique_for_date>, поэтому сможем формировать уникальные URL’ы, иcпользуя дату
    # публикации статей и slug. Django будет предотвращать создание нескольких статей с одинаковым слагом в один день
    slug = models.SlugField(max_length=250, unique_for_date='publish')

    # это поле является внешним ключом и определяет отношение
    # «один ко многим». Мы указываем, что каждая статья имеет автора, при-
    # чем каждый пользователь может быть автором любого количества ста-
    # тей. Для этого поля Django создаст в базе данных внешний ключ, исполь-
    # зуя первичный ключ связанной модели. В этом случае мы обращаемся
    # к модели User подсистемы аутентификации Django. Параметр on_delete
    # определяет поведение при удалении связанного объекта. Эта особен-
    # ность не специфична для Django, а взята из стандарта SQL. Используя
    # CASCADE, мы говорим, чтобы при удалении связанного пользователя база
    # данных также удаляла написанные им статьи. Вы можете посмотреть
    # все доступные опции на странице https://docs.djangoproject.com/en/2.0/
    # ref/models/fields/#django.db.models.ForeignKey.on_delete. Мы также указали
    # имя обратной связи от User к Post– параметр related_name. Так мы с лег-
    # костью получим доступ к связанным объектам автора. Позже мы более
    # подробно изучим эту тему;
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='blog_posts')

    # основное содержание статьи. Это текстовое поле, которое будет сохранено в столбце с типом TEXT в SQL базе данных;
    body = models.TextField()

    # поле даты, которое сохраняет дату публикации статьи. Мы используем функцию Django now для установки значения
    # по умолчанию. Она возвращает текущие дату и время. Вы можете рассматривать ее как стандартную функцию
    # datetime.now из Python, но с учетом временной зоны;
    publish = models.DateTimeField(default=timezone.now)

    # это поле даты указывает, когда статья была создана. Так как мы используем параметр
    # <auto_now_add>, дата будет сохраняться автоматически при создании объекта;
    created = models.DateTimeField(auto_now_add=True)

    # дата и время, указывающие на период, когда статья была отредактирована. Так как мы используем
    # параметр <auto_now,> дата будет сохраняться автоматически при сохранении объекта (update);
    updated = models.DateTimeField(auto_now=True)

    # это поле отображает статус статьи. Мы использовали параметр CHOICES, для того чтобы
    # ограничить возможные значения из указанного списка.
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Класс Meta внутри модели содержит метаданные. Мы указали Django порядок сортировки статей
    # по умолчанию – по убыванию даты публикации, поля publish. О том, что порядок убывающий,
    # говорит префикс «-». Таким образом, только что опубликованные статьи будут первыми в списке
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    objects = models.Manager()  # Менеджер по умолчанию
    published = PublishedManager()  # Новый менеджер

    # Мы можем использовать URL post_detail для построения канонического URL’а для объектов Post. В Django есть
    # соглашение о том, что метод модели get_absolute_url() должен возвращать канонический URL объекта.
    # Для реализации этого поведения мы будем использовать функцию reverse(),
    # которая дает возможность получать URL, указав имя шаблона и параметры.
    # Мы будем использовать метод get_absolute_url() в HTML-шаблонах, чтобы получать ссылку на статью.
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month,
                                                 self.publish.day, self.slug])
    tags = TaggableManager()


class Comment(models.Model):
    # Атрибут related_name позволяет получить доступ к комментариям конкретной статьи. Теперь мы сможем обращаться
    # к статье из комментария, используя запись comment.post, и к комментариям статьи при помощи post.comments.all().
    # Если бы мы не определили related_name, юзалось бы имя связанной модели с постфиксом _set (например, comment_set).
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)  # добавили булевое поле active, чтобы можно было скрывать комментарии

    class Meta:  # поле created для сортировки комментариев в хронологическом порядке.
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)

    # <END>

    # (about)
    # Django формирует имя таблицы, используя строчные назва-
    # ния приложения и модели (blog_post), но мы можем переопределить это имя
    # в классе Meta модели, используя атрибут db_table. Django автоматически создает
    # первичный ключ для каждой модели, но и это можно изменить, указав primary_
    # key=True для одного из полей модели. По умолчанию первичным ключом
    # является колонка id, которая заполняется целыми числами с автоинкремен-
    # том. Эта колонка соответствует полю id, которое добавляется автоматически
    # для всех моделей.