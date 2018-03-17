from django.contrib import sitemaps
from django.urls import reverse

from Fact import models


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['fact:sitemap_object', 'fact:sitemap_category']

    def location(self, item):
        return reverse(item)
