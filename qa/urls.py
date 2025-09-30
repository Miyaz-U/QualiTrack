from django.contrib import admin
from django.urls import path
from qa import views

urlpatterns = [
    path("", views.home, name="home"),
    path("userstories/", views.userstories_view, name="userstories"),
    path("defects/", views.defects_view, name="defects"),
    path("testcases/", views.testcases_view, name="testcases"),
    path("efforts/", views.efforts_view, name="efforts"),
    path("userstories-for-sprint/", views.userstories_for_sprint, name="userstories_for_sprint"),
    path("upload/", views.upload_file, name="upload_file"),
]
