from django.urls import path, include
from .views import (
    PDFMediaSecureView
    )

app_name = 'pdf_app'

urlpatterns = [
    path('media/pdf_files/<str:file>', PDFMediaSecureView.as_view(), name='pdf_media_secure'),
]
