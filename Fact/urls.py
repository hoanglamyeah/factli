from django.conf.urls import url
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from Fact import models
from Fact.sitemaps import StaticViewSitemap
from django.contrib.auth.models import User
from . import views

sitemaps = {
    'static': StaticViewSitemap,
}

map_object = {
    'queryset': models.Object.objects.all().order_by('-id'),
    'date_field': 'pub_date',
}

map_category = {
    'queryset': models.Category.objects.all().order_by('-id'),
}

urlpatterns = [
    url(r'^test/$', views.test, name='page_test'),
    url(r'^manager/import/$', views.import_data, name='import_data'),
    url(r'^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^support/$', views.page_support, name='page_support'),
    url(r'^faq/$', views.page_faq, name='page_faq'),
    url(r'^term/$', views.page_term, name='page_term'),
    url(r'^career/$', views.page_career, name='page_career'),
    url(r'^category/$', views.archive_index, name='category_index'),
    url(r'^member/$', views.member_index, name='member_index'),
    url(r'^member/(?P<member_id>[0-9]+)/$', views.member_get, name='member_get'),
    url(r'^(?P<slug>[\w-]+)/$', views.get_object, name='object_show'),
    url(r'^(?P<slug>[\w-]+)/(?P<fact_id>[0-9]+)/$', views.fact_get, name='fact_show'),
    url(r'^category/(?P<slug>[\w-]+)/$', views.archive_detail, name='category_show'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-object.xml', sitemap,
         {'sitemaps': {'blog': GenericSitemap(map_object, priority=0.6)}},
         name='sitemap_object'),
    path('sitemap-category.xml', sitemap,
         {'sitemaps': {'blog': GenericSitemap(map_category, priority=0.6)}},
         name='sitemap_category'),
    path('sitemap-category.xml', sitemap,
         {'sitemaps': {'blog': GenericSitemap(map_category, priority=0.6)}},
         name='sitemap_category'),
]
