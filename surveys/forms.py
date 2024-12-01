from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Survey, Question, Option, Profile

class CustomUserCreationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    ROLE_CHOICES=[
        ('creator', 'Survey Creator'),
        ('taker', 'Survey Taker'),
        
    ]
    role=forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model=User
        fields=('username', 'email', 'password1', 'password2', 'role')

    def save(self,commit=True):
        user=super().save(commit=False)
        user.email=self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user,role=self.cleaned_data['role'])
        return user

class SurveyCreationForm(forms.ModelForm):
    class Meta:
        model=Survey
        fields=['title', 'description']  

class QuestionForm(forms.ModelForm):
    class Meta:
        model=Question
        fields=['text', 'question_type']  

class OptionForm(forms.ModelForm):
    class Meta:
        model=Option
        fields=['text']  