from django.conf.urls import url

from . import views

urlpatterns = [
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
]
