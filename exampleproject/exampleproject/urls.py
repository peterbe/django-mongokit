from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    (r'^exampleapp/', include('exampleproject.exampleapp.urls')),
    (r'^exampleapp_sql/', include('exampleproject.exampleapp_sql.urls', namespace='sql',
                                  app_name='exampleapp_sql')),
    (r'^benchmarker/', include('exampleproject.benchmarker.urls')),
)
