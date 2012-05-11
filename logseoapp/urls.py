from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from logseoapp.views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^testing/$', 'logseoapp.views.show_object'),
    url(r'^ranks/$', 'logseoapp.views.get_ranks'),
    (r'^phrase/(\d{1,6})/$', 'logseoapp.views.get_phrase'),
    # Examples:
    # url(r'^$', 'logseo.views.home', name='home'),
    # url(r'^logseo/', include('logseo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
