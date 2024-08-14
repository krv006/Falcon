from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path("", include('apps.urls')),
                  path("ckeditor5/", include('django_ckeditor_5.urls')),
                  path('accounts/', include('allauth.urls')),
              ] + debug_toolbar_urls() + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL,
                                                                                              document_root=STATIC_ROOT)
