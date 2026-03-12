from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя',
                'class': 'comment-input'
            }),
            'text': forms.Textarea(attrs={
                'placeholder': 'Ваши мысли...',
                'class': 'comment-area',
                'rows': 3
            }),
        }
