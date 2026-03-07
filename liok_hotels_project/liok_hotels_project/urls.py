from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from liok_hotels_app.sitemap import StaticViewSitemap, PropertySitemap, BlogSitemap, RoomSitemap
from django.http import HttpResponse
import os


sitemaps = {
    'pages': StaticViewSitemap,
    'properties': PropertySitemap,
    'blogs': BlogSitemap,
    'rooms': RoomSitemap,
}


def robots_txt(request):
    file_path = os.path.join(settings.BASE_DIR, 'liok_hotels_project', 'robots.txt')
    with open(file_path, 'r') as f:
        return HttpResponse(f.read(), content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('liok_hotels_app.urls')),

    path('robots.txt', robots_txt),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)