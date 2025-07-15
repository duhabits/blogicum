from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Post
from django.contrib.auth import get_user_model

from .models import Comment

User = get_user_model()


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'location', 'category', 'image']
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date and pub_date.date() < timezone.now().date():
            raise ValidationError("Дата публикации не может быть в прошлом")
        return pub_date


class CongratulationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
