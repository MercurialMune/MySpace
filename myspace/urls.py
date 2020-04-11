from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .feeds import PostsFeed

urlpatterns = [
    url(r'^$', views.post_list_view, name='post_list_view'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<post>[-\w]+)/$', views.post_detail_view, name='post_detail_view'),
    url(r'^search/', views.search_results, name='search_results'),
    url(r'^feed/$', PostsFeed(), name='post_feed')
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)