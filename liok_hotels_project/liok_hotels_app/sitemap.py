from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Property, Blog, RoomCategory


class StaticViewSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return [
            "admin_pages:home",
            "admin_pages:about",
            "admin_pages:properties_all",
            "admin_pages:rooms",
            "admin_pages:blog_list_public",
            "admin_pages:gallery",
            "admin_pages:contact",
            "admin_pages:book_now",
            "admin_pages:nearby_attractions",
        ]

    def location(self, item):
        return reverse(item)


class PropertySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Property.objects.all()

    def location(self, obj):
        return reverse("admin_pages:property_detail", kwargs={"slug": obj.slug})


class BlogSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Blog.objects.all()

    def location(self, obj):
        return reverse("admin_pages:blog_detail_public", kwargs={"slug": obj.slug})


class RoomSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return RoomCategory.objects.all()

    def location(self, obj):
        return reverse("admin_pages:room_detail", kwargs={"pk": obj.pk})