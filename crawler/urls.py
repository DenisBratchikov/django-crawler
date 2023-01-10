from django.urls import path

from .views import Main

app_name = "crawler"
urlpatterns = [
    path("", Main().index, name="index")
]
