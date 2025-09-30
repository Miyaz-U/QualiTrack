from django.contrib import admin
from .models import Sprint, UserStory, TestCase, TestResult, Defect, Comment, Effort

admin.site.register([Sprint, UserStory, TestCase, TestResult, Defect, Comment, Effort])