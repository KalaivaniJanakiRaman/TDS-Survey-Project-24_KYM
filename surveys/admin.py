from django.contrib import admin

# Register your models here.
from .models import Survey, Question, Option, Response, Profile

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Response)
admin.site.register(Profile)