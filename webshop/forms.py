from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Developer, Game

class GameForm(forms.ModelForm):
    def clean(self):
        super().clean()
        if "genres" in self.cleaned_data and self.cleaned_data["genres"].count() > 3:
            raise ValidationError({"genres": "Pick three genres at most"})

    class Meta:
        model = Game
        fields = 'slug', 'name', 'image', 'url', 'price', 'description', 'genres',
        widgets = dict(genres=forms.CheckboxSelectMultiple)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'email',

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = 'username', 'password1', 'password2', 'email',

class DeveloperForm(forms.ModelForm):
    class Meta:
        model = Developer
        fields = 'slug', 'name', 'description',
