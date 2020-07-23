from django import forms
from .models import Comment

# Django предоставляет два базовых класса для форм: Form и ModelForm


class EmailPostForm(forms.Form):
    # Поле name имеет тип CharField. Этот тип полей будет отображаться как элемент <inputtype="text">
    name = forms.CharField(max_length=25)

    # поля EmailField имеют валидацию и могут получать только корректные адреса
    email = forms.EmailField()
    to = forms.EmailField()

    # Каждый тип по умолчанию имеет виджет для отображения в HTML. Виджет может быть изменен с помощью параметра widget.
    # В поле comments мы используем виджет Textarea
    # для отображения HTML-элемента <textarea> вместо стандартного <input>
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    # Все, что нужно для создания формы из модели, – указать, какую модель использовать в опциях класса Meta.
    # Django найдет нужную модель и автоматически построит форму.
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')

    # <END>

    # Мы определили максимальную
    # длину в 25 символов для поля name и сделали поле comments необязательным,
    # указав required=False. Все это учитывается при валидации формы. Использу-
    # емые в этом примере поля являются лишь малой частью подсистемы форм
    # Django. Для того чтобы увидеть полный список и описания, можете перейти на
    # страницу https://docs.djangoproject.com/en/2.0/ref/forms/fields/.