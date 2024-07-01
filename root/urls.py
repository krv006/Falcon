from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from root.settings import MEDIA_URL, MEDIA_ROOT,STATIC_URL, STATIC_ROOT

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path("", include('apps.urls')),
              ] + static(MEDIA_URL, document_root=MEDIA_ROOT) + static(STATIC_URL, document_root=STATIC_ROOT)