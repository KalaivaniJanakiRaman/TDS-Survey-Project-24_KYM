from django.db import models
from django.contrib.auth.models import User
    

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ROLE_CHOICES=[
        ('creator', 'Survey Creator'),
        ('taker', 'Survey Taker'),
    ]
    role=models.CharField(max_length=10,choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Survey(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    creator=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('republished', 'Republished'),  
    ]
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='draft')

    def __str__(self):
        return self.title

class Question(models.Model):
    survey=models.ForeignKey(Survey,related_name='questions',on_delete=models.CASCADE)
    text=models.TextField()
    QUESTION_TYPES=[
        ('radio', 'Radio'),
        ('checkbox', 'Checkbox'),
    ]
    question_type=models.CharField(max_length=20,choices=QUESTION_TYPES)

    def __str__(self):
        return self.text

class Option(models.Model):
    question=models.ForeignKey(Question,related_name='options',on_delete=models.CASCADE)
    text=models.CharField(max_length=200)

    def __str__(self):
        return self.text
    
from django.utils import timezone

class Response(models.Model):
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_option=models.ForeignKey(Option,on_delete=models.CASCADE)
    created_at=models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together=['survey','user','question']

    def __str__(self):
        return f"{self.user.username} response to {self.question.text} in {self.survey.title}"