from django.urls import path
from django.views.generic import TemplateView

from .views import upload

app_name = 'imgrecognition'

urlpatterns = [
    path('', TemplateView.as_view(template_name='imgrecognition/index.html')),
    path('upload/', upload.upload, name='upload'),
]