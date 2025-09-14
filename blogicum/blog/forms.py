from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date and pub_date.date() < timezone.now().date():
            raise ValidationError('Дата публикации не может быть в прошлом')
        return pub_date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['pub_date'] = timezone.now()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
