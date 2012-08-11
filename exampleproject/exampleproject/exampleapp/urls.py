from django.conf.urls.defaults import patterns, url
import views


urlpatterns = patterns('',
        url(r'^$', views.homepage, name='homepage'),
        url(r'^delete/(?P<_id>[\w-]+)$', views.delete_talk, name='delete_talk'),
)
