from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('admin_td/', admin.site.urls),
    
    path('', include('pdf_app.urls', namespace='pdf_app')),

    # path('', include('users.urls', namespace='users')),
    path('', include('core.urls', namespace='core')),

    path('api/', include('api.urls', namespace='api')),
]



admin.site.site_header = "Text Intent Classifier"
admin.site.site_title = f"Text Intent Classifier Admin Portal"
admin.site.index_title = f"Welcome to Text Intent Classifier"


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + [path('__debug__/', include('debug_toolbar.urls')),]

