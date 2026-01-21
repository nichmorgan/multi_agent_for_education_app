from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ingest/", include("ingest.urls")),
    path("knowledge/", include("knowledge.urls")),
    path("agents/", include("agents.urls")),
    path("", include("ingest.urls")),  # Default to ingest for MVP
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
