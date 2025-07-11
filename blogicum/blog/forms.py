from django import forms

from .models import Comment


class CongratulationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
