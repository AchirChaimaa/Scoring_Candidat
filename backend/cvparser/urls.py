from django.urls import path
from .views import ExtractCVView

urlpatterns = [
    path('upload-cv/', ExtractCVView.as_view(), name='upload-cv'),
]
