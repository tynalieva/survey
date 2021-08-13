from django import forms
from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'category', 'description', 'region', 'address', )


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image', )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body', )
